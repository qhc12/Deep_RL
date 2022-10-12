class PresetRoad:
    """
    Holds preferences/values for a predefined road. Currently can hold:
        - Road parts (with road type and length)
        - Static events (with event type and start and end)
        - Dynamic events (with event type and start and end).
    Any of the above defined values override any preferences defined in the config file.
    """

    def __init__(self, config, route_data, **entries):
        self.route_data = route_data if route_data else None

        self.__dict__.update(entries)
        # Update the config entries with the entries from the parsed road file
        if self.includes_road():
            config.road_length = sum(entry[1] for entry in self.road)

        config.includes_route_data = self.includes_route_data()

    def includes_road(self):
        """
        Returns true if the road file includes a road entry with road parts.
        """
        return 'road' in self.__dict__

    def includes_static_events(self):
        """
        Returns True if the road file includes an entry for static events.
        """
        return 'static_events' in self.__dict__

    def includes_dynamic_events(self):
        """
        Returns True if the road file includes an entry for dynamic events.
        """
        return 'dynamic_events' in self.__dict__

    def includes_route_data(self):
        """
        Returns True if route data is included.
        """
        return self.route_data is not None
