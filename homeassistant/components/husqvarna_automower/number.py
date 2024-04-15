"""Creates a number entity for the cutting height of the mower."""

import logging

from aioautomower.exceptions import ApiException

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AutomowerDataUpdateCoordinator
from .entity import AutomowerControlEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up number platform."""
    coordinator: AutomowerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AutomowerNumberEntity(mower_id, coordinator)
        for mower_id in coordinator.data
    )


class AutomowerNumberEntity(AutomowerControlEntity, NumberEntity):
    """Defining the cutting height entity."""
    
    _attr_category = EntityCategory.CONFIG
    _attr_translation_key = "cutting_height"
    _attr_native_min_value = 1
    _attr_native_max_value = 9
    _attr_native_step = 1

    def __init__(
        self,
        mower_id: str,
        coordinator: AutomowerDataUpdateCoordinator,
    ) -> None:
        """Set up number platform."""
        super().__init__(mower_id, coordinator)
        self._attr_unique_id = f"{mower_id}_cutting_height"

    @property
    def current_option(self) -> int | None:
        """Return the current value for the entity."""
        return self.mower_attributes.cutting_height

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self.coordinator.api.set_cutting_height(self.mower_id, int(value))
        except ApiException as exception:
            raise HomeAssistantError(
                f"Command couldn't be sent to the command queue: {exception}"
            ) from exception
