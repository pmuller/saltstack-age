# __builtins__.pyi

from typing import Any, Callable, Dict

# __salt__ is typically a dictionary of all the Salt execution modules available (functions).
__salt__: Dict[str, Callable[..., Any]]

# __opts__ is a dictionary containing the configuration options for the minion or master.
__opts__: Dict[str, Any]

# __grains__ contains the static grains of the system.
__grains__: Dict[str, Any]

# __pillar__ is a dictionary that contains the pillar data for the minion.
__pillar__: Dict[str, Any]

# __context__ is a dictionary where data can be stored temporarily for the life of a Salt command.
__context__: Dict[str, Any]

# __runner__ is a dictionary of runner modules (only available in runners).
__runner__: Dict[str, Callable[..., Any]]

# __sdb__ provides access to Salt's SDB (Salt database).
__sdb__: Dict[str, Callable[..., Any]]

# __ret__ might be used to contain return data in some contexts.
__ret__: Dict[str, Any]

# Example additional dunders that might be available in specific modules or under certain contexts:
# __master_opts__ for master configuration options (in salt master extensions)
__master_opts__: Dict[str, Any]

# __proxy__ for proxy minions
__proxy__: Dict[str, Callable[..., Any]]

# __mine__ for accessing mine functions and data
__mine__: Dict[str, Callable[..., Any]]
