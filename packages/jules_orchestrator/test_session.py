import pytest
from hypothesis import given, strategies as st
from unittest.mock import MagicMock, call, patch

from jules_orchestrator.client import JulesClient, JulesAPIError
from jules_orchestrator.session import JulesSession

@given(
    source_name=st.text(min_size=1),
    automation_mode=st.sampled_from(["AUTO_CREATE_PR", "MANUAL", "INTERACTIVE"]),
    task_description=st.text(),
)
def test_jules_session_initialization(source_name, automation_mode, task_description):
    """Test deterministic initialization of JulesSession without external calls."""
    mock_client = MagicMock(spec=JulesClient)
    session = JulesSession(
        client=mock_client,
        source_name=source_name,
        automation_mode=automation_mode,
        task_description=task_description,
    )
    
    assert session.session_name is None
    assert session.get_status() == "UNINITIALIZED"
    mock_client.create_session.assert_not_called()

@given(
    session_name=st.text(min_size=1),
    state=st.sampled_from(["CONNECTING", "PENDING_APPROVAL", "ACTIVE", "COMPLETED", "FAILED", "NEEDS_APPROVAL"])
)
def test_jules_session_start_and_status(session_name, state):
    """Test start and status polling deterministic behavior."""
    mock_client = MagicMock(spec=JulesClient)
    mock_client.create_session.return_value = {"name": session_name, "state": "CONNECTING"}
    mock_client.get_session.return_value = {"name": session_name, "state": state}
    
    session = JulesSession(client=mock_client, source_name="test_source")
    
    # Test start
    session_data = session.start()
    assert session_data["name"] == session_name
    assert session.session_name == session_name
    mock_client.create_session.assert_called_once()
    
    # Test get_status
    status = session.get_status()
    assert status == state
    mock_client.get_session.assert_called_once_with(session_name)

def test_jules_session_approve_plan_uninitialized():
    """Ensure approving a plan fails if uninitialized."""
    mock_client = MagicMock(spec=JulesClient)
    session = JulesSession(client=mock_client, source_name="test_source")
    
    with pytest.raises(JulesAPIError, match="Session not initialized."):
        session.approve_plan("Approval message")

@given(
    session_name=st.text(min_size=1),
    message=st.text()
)
def test_jules_session_approve_plan(session_name, message):
    """Test approve plan deterministic routing."""
    mock_client = MagicMock(spec=JulesClient)
    mock_client.approve_plan.return_value = {"name": session_name, "state": "ACTIVE"}
    
    session = JulesSession(client=mock_client, source_name="test_source", session_name=session_name)
    result = session.approve_plan(message=message)
    
    assert result["state"] == "ACTIVE"
    mock_client.approve_plan.assert_called_once_with(session_name, message=message)

def test_jules_session_interact_uninitialized():
    """Ensure interacting fails if uninitialized."""
    mock_client = MagicMock(spec=JulesClient)
    session = JulesSession(client=mock_client, source_name="test_source")
    
    with pytest.raises(JulesAPIError, match="Session not initialized."):
        session.interact("Hello")

@given(
    session_name=st.text(min_size=1),
    text=st.text()
)
def test_jules_session_interact(session_name, text):
    """Test interact method."""
    mock_client = MagicMock(spec=JulesClient)
    mock_client.interact.return_value = {"name": session_name, "state": "ACTIVE"}
    
    session = JulesSession(client=mock_client, source_name="test_source", session_name=session_name)
    result = session.interact(text)
    
    assert result["state"] == "ACTIVE"
    mock_client.interact.assert_called_once_with(session_name, text)

@patch("jules_orchestrator.session.time.time")
@patch("jules_orchestrator.session.time.sleep")
def test_jules_session_poll_timeout(mock_sleep, mock_time):
    """Test that run_auto_pr_workflow raises a timeout error."""
    mock_client = MagicMock(spec=JulesClient)
    session_name = "test_session_123"
    mock_client.create_session.return_value = {"name": session_name, "state": "CONNECTING"}
    mock_client.get_session.return_value = {"name": session_name, "state": "CONNECTING"}
    
    session = JulesSession(client=mock_client, source_name="test_source")
    
    import itertools
    mock_time.side_effect = itertools.count(0, 100)
    
    with pytest.raises(JulesAPIError, match="Workflow timeout after 600 seconds"):
        session.run_auto_pr_workflow(timeout=600, interval=10)
        
def test_jules_session_http_faults_and_401s():
    """Test session behavior under simulated network faults and 401 Unauthorized errors."""
    mock_client = MagicMock(spec=JulesClient)
    mock_client.create_session.side_effect = JulesAPIError("401 Unauthorized")
    
    session = JulesSession(client=mock_client, source_name="test_source")
    
    with pytest.raises(JulesAPIError, match="401 Unauthorized"):
        session.start()
        
    mock_client.create_session.assert_called_once()
    
    mock_client.create_session.side_effect = JulesAPIError("503 Service Unavailable")
    with pytest.raises(JulesAPIError, match="503 Service Unavailable"):
        session.start()

@patch("jules_orchestrator.session.time.time")
@patch("jules_orchestrator.session.time.sleep")
def test_jules_session_run_auto_pr_workflow_happy_path(mock_sleep, mock_time):
    """Test the happy path of run_auto_pr_workflow where it completes successfully."""
    mock_client = MagicMock(spec=JulesClient)
    session_name = "test_session_happy"
    mock_client.create_session.return_value = {"name": session_name, "state": "CONNECTING"}
    
    # Simulate state transitions: CONNECTING -> NEEDS_APPROVAL -> ACTIVE -> COMPLETED
    mock_client.get_session.side_effect = [
        {"name": session_name, "state": "CONNECTING"},
        {"name": session_name, "state": "NEEDS_APPROVAL"},
        {"name": session_name, "state": "ACTIVE"},
        {"name": session_name, "state": "COMPLETED"},
    ]
    
    mock_client.approve_plan.return_value = {"name": session_name, "state": "ACTIVE"}
    
    session = JulesSession(client=mock_client, source_name="test_source")
    
    import itertools
    mock_time.side_effect = itertools.count(0, 1) # Advance time slightly
    
    # Track if callback was called
    callback_called = False
    def mock_approval_callback(data):
        nonlocal callback_called
        callback_called = True
        return True
        
    result = session.run_auto_pr_workflow(plan_approval_callback=mock_approval_callback, timeout=600, interval=10)
    
    assert result["state"] == "COMPLETED"
    assert callback_called is True
    mock_client.approve_plan.assert_called_once_with(session_name, message="Approved via auto PR workflow")

@patch("jules_orchestrator.session.time.time")
@patch("jules_orchestrator.session.time.sleep")
def test_jules_session_run_auto_pr_workflow_malformed_payload(mock_sleep, mock_time):
    """Test behavior when the payload state is malformed or missing."""
    mock_client = MagicMock(spec=JulesClient)
    session_name = "test_session_malformed"
    mock_client.create_session.return_value = {"name": session_name, "state": "CONNECTING"}
    
    # Return malformed/unexpected data 
    mock_client.get_session.side_effect = [
        {"name": session_name, "status_wrong_key": "CONNECTING"}, # Missing 'state' key
        {"name": session_name, "state": "UNEXPECTED_STATE_STRING"},
        {"name": session_name, "state": "COMPLETED"}
    ]
    
    session = JulesSession(client=mock_client, source_name="test_source")
    
    import itertools
    mock_time.side_effect = itertools.count(0, 1)
    
    result = session.run_auto_pr_workflow(timeout=600, interval=10)
    
    # It should gracefully handle the missing/unexpected keys because session.py uses `.get("state", "UNKNOWN")`
    assert result["state"] == "COMPLETED"
