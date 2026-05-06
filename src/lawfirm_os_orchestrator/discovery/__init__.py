"""Local-only Research Radar discovery imports."""

from lawfirm_os_orchestrator.discovery.local_import import import_signal, list_signals
from lawfirm_os_orchestrator.discovery.models import DiscoverySignal

__all__ = ["DiscoverySignal", "import_signal", "list_signals"]
