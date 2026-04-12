from src.agents.scientific.scientific_agent import ScientificAgent
from src.agents.v8_core import Task


def test_scientific_agent_protein_task():
    agent = ScientificAgent("Sci-Test")
    task = Task("ScientificResearch", "Search for protein structure of Hemoglobin")

    finding = agent.execute_task(task)

    assert "AlphaFold DB" in finding.content
    assert "hemoglobin" in finding.content
    assert "science" in finding.tags


def test_scientific_agent_chem_task():
    agent = ScientificAgent("Sci-Test")
    task = Task("ScientificResearch", "Analyze water molecule")

    finding = agent.execute_task(task)

    assert "PubChem" in finding.content
    assert "water" in finding.content


def test_scientific_agent_wrong_task_type():
    agent = ScientificAgent("Sci-Test")
    task = Task("DataAnalysis", "Wrong task type")

    finding = agent.execute_task(task)

    assert "Task type mismatch" in finding.content
