"""QWebChannel bridge for Python <-> JavaScript communication."""

from PySide6.QtCore import QObject, Slot, Signal


class ChartBridge(QObject):
    """Bridge object exposed to JavaScript via QWebChannel."""

    # Signal emitted when JS requests data
    data_requested = Signal(str, str)  # (chart_id, params_json)

    # Signal emitted when JS reports a chart event (click, etc.)
    chart_event = Signal(str, str)  # (event_type, data_json)

    @Slot(str, str)
    def requestData(self, chart_id: str, params: str):
        """Called from JS when a chart needs data."""
        self.data_requested.emit(chart_id, params)

    @Slot(str, str)
    def onChartEvent(self, event_type: str, data: str):
        """Called from JS when a chart interaction occurs."""
        self.chart_event.emit(event_type, data)

    @Slot(result=str)
    def ping(self) -> str:
        """Health check from JS."""
        return "pong"
