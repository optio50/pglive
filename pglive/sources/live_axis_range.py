from copy import copy
from typing import Optional, List, Tuple


class LiveAxisRange:

    def __init__(self, roll_on_tick: int = 1, offset_left: float = 0., offset_right: float = 0., offset_top: float = 0.,
                 offset_bottom: float = 0., fixed_range: Optional[List[float]] = None) -> None:
        self.roll_on_tick = roll_on_tick
        self.offset_left = offset_left
        self.offset_right = offset_right
        self.offset_top = offset_top
        self.offset_bottom = offset_bottom
        self.crop_left_offset_to_data = False
        self.crop_right_offset_to_data = False
        self.crop_top_offset_to_data = False
        self.crop_bottom_offset_to_data = False
        self.fixed_range = fixed_range
        self.x_range = {}
        self.y_range = {}
        self.final_x_range = [0, 0]
        self.final_y_range = [0, 0]
        self.ignored_data_connectors = []

    def get_x_range(self, data_connector, tick: int) -> List[float]:
        axis_range = data_connector.plot.data_bounds(ax=0, offset=self.roll_on_tick if self.roll_on_tick > 1 else 0)
        x, _ = data_connector.plot.getData()

        final_range = self._get_range(axis_range, tick, (self.offset_left, self.offset_right))
        if final_range is None:
            return self.final_x_range
        offset_x = data_connector.plot.pos().x()
        final_range[0] += offset_x
        final_range[1] += offset_x
        # Check left and right offset and crop to data if flag is set
        if self.crop_left_offset_to_data and final_range[0] < x[0]:
            final_range[0] = x[0]
        if self.crop_right_offset_to_data and final_range[1] > x[-1]:
            final_range[1] = x[-1]
        self.x_range[data_connector.__hash__()] = copy(final_range)
        for connector_id, x_range in self.x_range.items():
            if connector_id in self.ignored_data_connectors:
                continue
            if final_range[0] > x_range[0]:
                final_range[0] = x_range[0]
            if final_range[1] < x_range[1]:
                final_range[1] = x_range[1]
        if final_range[0] == final_range[1]:
            # Pyqtgraph ViewBox.setRange doesn't like same value for min and max,
            # therefore in that case we must set some range
            final_range[0] -= 0.4
            final_range[1] += 0.4
        if self.final_x_range != final_range:
            self.final_x_range = final_range
        return self.final_x_range

    def get_y_range(self, data_connector, tick: int) -> List[float]:
        axis_range = data_connector.plot.data_bounds(ax=1, offset=self.roll_on_tick if self.roll_on_tick > 1 else 0)
        _, y = data_connector.plot.getData()
        final_range = self._get_range(axis_range, tick, (self.offset_bottom, self.offset_top))
        if final_range is None:
            return self.final_y_range
        offset_y = data_connector.plot.pos().y()
        final_range[0] += offset_y
        final_range[1] += offset_y
        # Check left and right offset and crop to data if flag is set
        if self.crop_bottom_offset_to_data and final_range[0] < y[0]:
            final_range[0] = y[0]
        if self.crop_top_offset_to_data and final_range[1] > y[-1]:
            final_range[1] = y[-1]
        self.y_range[data_connector.__hash__()] = copy(final_range)
        for connector_id, y_range in self.y_range.items():
            if connector_id in self.ignored_data_connectors:
                continue
            if final_range[0] > y_range[0]:
                final_range[0] = y_range[0]
            if final_range[1] < y_range[1]:
                final_range[1] = y_range[1]
        if final_range[0] == final_range[1]:
            # Pyqtgraph ViewBox.setRange doesn't like same value for min and max,
            # therefore in that case we must set some range
            final_range[0] -= 0.4
            final_range[1] += 0.4
        if self.final_y_range != final_range:
            self.final_y_range = final_range
        return self.final_y_range

    def _get_range(self, axis_range: Tuple[float, float], tick: int, offsets: Tuple[float, float]) -> List[float]:
        if self.fixed_range is not None:
            return self.fixed_range
        elif self.roll_on_tick == 1:
            return [axis_range[0], axis_range[1]]
        elif tick % self.roll_on_tick == 0 or tick < 2:
            range_width = abs(axis_range[1] - axis_range[0])
            if tick < 2:
                range_width = range_width * (self.roll_on_tick - (tick + 1))
                return [axis_range[1], axis_range[1] + range_width]
            else:
                return [axis_range[1] - range_width * offsets[0], (axis_range[1] + range_width) + (
                        range_width * offsets[1])]

    def ignore_connector(self, data_connector, flag: bool) -> None:
        if not flag:
            self.ignored_data_connectors.append(data_connector.__hash__())
        else:
            self.ignored_data_connectors.remove(data_connector.__hash__())
        try:
            self.get_x_range(data_connector, data_connector.rolling_index)
        except TypeError:
            return None
        try:
            self.get_y_range(data_connector, data_connector.rolling_index)
        except TypeError:
            return None
