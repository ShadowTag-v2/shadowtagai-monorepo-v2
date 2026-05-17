from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static


class JudgeSixApp(App):
  """A Textual app to monitor Judge#6 governance enforcement."""

  CSS_PATH = "app.tcss"
  BINDINGS = [
    Binding("d", "toggle_dark", "Toggle Dark Mode"),
    Binding("q", "quit", "Quit"),
  ]

  def compose(self) -> ComposeResult:
    """Create child widgets for the app."""
    yield Header()
    yield Container(
      Static("Judge#6 Governance Monitor", classes="title"),
      Static("Waiting for data...", id="status"),
      id="main-container",
    )
    yield Footer()

  def action_toggle_dark(self) -> None:
    """An action to toggle dark mode."""
    self.dark = not self.dark


if __name__ == "__main__":
  app = JudgeSixApp()
  app.run()
