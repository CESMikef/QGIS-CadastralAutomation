"""
Cadastral Automation Plugin
"""

def classFactory(iface):
    """Load CadastralAutomation class from file cadastral_automation.
    
    Args:
        iface: A QGIS interface instance.
    """
    from .cadastral_automation import CadastralAutomation
    return CadastralAutomation(iface)
