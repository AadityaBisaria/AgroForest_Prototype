from typing import List, Tuple, Any, Dict,Optional


GLOBAL_GROWTH_MASKS: Dict[str, List[List[int]]] = {
    "seedling": [
        [1] # 1x1
    ],
    "bush": [
        [1, 1],
        [1, 0] # 2x2 bounding box
    ],
    "mature_tree": [ # The irregular shape requested (3x3 bounding box)
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 0] 
    ]
}



class PlatformObject:
    """
    Base class for any item to be placed on the TilePlatform.
    It enforces the required properties for placement.
    """
    def __init__(self, obj_id: str, width_tiles: int, length_tiles: int,shape_mask: Optional[List[List[int]]] = None):
        if not obj_id:
             raise ValueError("Object must have a unique ID.")
        self.id = obj_id
        # Renaming x_tile/y_tile for clarity in context of width/length
        self.width_tiles = width_tiles
        self.length_tiles = length_tiles
        self.x_coord: int = -1 
        self.y_coord: int = -1

        if shape_mask is None:
            # Default to a solid rectangle mask if none provided
            self.shape_mask = [[1] * width_tiles for _ in range(length_tiles)]
        else:
            # Basic validation of the custom mask dimensions
            if len(shape_mask) != length_tiles or any(len(row) != width_tiles for row in shape_mask):
                raise ValueError("Shape mask dimensions must match width_tiles and length_tiles.")
            self.shape_mask = shape_mask

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID='{self.id}', Dim={self.width_tiles}x{self.length_tiles})"

class TilePlatform:
    """
    Manages a 2D grid and allows placing PlatformObject instances.
    """
    def __init__(self, width: int, length: int):
        """
        Initializes the platform grid and object storage.
        """
        if width <= 0 or length <= 0:
            raise ValueError("Width and length must be positive integers.")

        self.width = width
        self.length = length
        self.grid: List[List[Any]] = [[0] * width for _ in range(length)]
        self.objects: Dict[str, PlatformObject] = {}
        
        print(f"--- Platform Initialized: {width}x{length} tiles ---")


    def _is_valid_position(self, start_x: int, start_y: int, obj_width: int, obj_length: int) -> bool:
        """
        Checks if the required tile area is within the platform boundaries.
        (Implementation remains the same)
        """
        if start_x < 0 or start_y < 0:
            return False
            
        if start_x + obj_width > self.width or start_y + obj_length > self.length:
            return False
            
        return True


    def _is_area_free(self, start_x: int, start_y: int, obj_width: int, obj_length: int) -> bool:
        """
        Checks if all tiles required by the object are currently empty (value is 0).
        (Implementation remains the same)
        """
        for y in range(start_y, start_y + obj_length):
            for x in range(start_x, start_x + obj_width):
                if self.grid[y][x] != 0:
                    return False
        return True


    def place_object(self, start_x: int, start_y: int, obj: PlatformObject) -> bool:
        """
        Attempts to place a PlatformObject instance onto the platform,
        storing the object instance itself in the grid cells.
        """
        obj_id = obj.id
        obj_width = obj.width_tiles
        obj_length = obj.length_tiles

        # 1. Check for Duplicate ID
        if obj_id in self.objects:
            print(f"Error: Object ID '{obj_id}' is already present on the platform. Cannot place duplicates.")
            return False

        # 2. Check for Boundary Conditions
        if not self._is_valid_position(start_x, start_y, obj_width, obj_length):
            print(f"Error: Object '{obj_id}' ({obj_width}x{obj_length}) does not fit at ({start_x}, {start_y}). Out of bounds.")
            return False

        # 3. Check for Collision (Area Free)
        # Note: _is_area_free still works because it checks for '!= 0'
        if not self._is_area_free(start_x, start_y, obj_width, obj_length):
            print(f"Error: Object '{obj_id}' ({obj_width}x{obj_length}) cannot be placed at ({start_x}, {start_y}). Area is already occupied.")
            return False

        # 4. Place the object on the grid
        for y in range(start_y, start_y + obj_length):
            for x in range(start_x, start_x + obj_width):
                # *** CORRECTED IMPLEMENTATION: Store the object instance ***
                self.grid[y][x] = obj
        
        # 5. Store the object instance in the lookup dictionary
        self.objects[obj_id] = obj
        
        # 6. Update the object's internal coordinates
        obj.x_coord = start_x 
        obj.y_coord = start_y 
        
        print(f"Success: Placed object '{obj_id}' ({obj_width}x{obj_length}) at ({start_x}, {start_y}).")
        return True
        
    def get_object_instance(self, obj_id: str) -> PlatformObject | None:
        """Retrieves the actual object instance by its ID."""
        return self.objects.get(obj_id)

    def display(self):
        print("\n--- Platform Grid (Y=Row, X=Column) ---")
        
        display_grid: List[List[str]] = []
        max_len = 1 

        for row in self.grid:
            display_row = []
            for cell_value in row:
                if cell_value == 0:
                    # Cell is empty
                    display_val = "."
                elif isinstance(cell_value, PlatformObject):
                    # Cell contains an object instance
                    obj_id = cell_value.id
                    # Safely get the name property if it exists (for Plant)
                    obj_name = getattr(cell_value, 'name', obj_id) 
                    display_val = f"{obj_id}/{obj_name}"
                else:
                    # Cell contains some other unexpected type (e.g., a number, a simple string)
                    display_val = str(cell_value)
                
                display_row.append(display_val)
                max_len = max(max_len, len(display_val))
            display_grid.append(display_row)
        # Print the column header (X-axis)
        header = "   " + " ".join([f"{i:>{max_len}}" for i in range(self.width)])
        print(header)
        print("  " + "-" * (len(header) - 3))

        # Print the grid rows
        for i, row in enumerate(self.grid):
            # Print the row header (Y-axis)
            row_str = f"{i:<2}|"
            
            # Print the cells in the row
            for cell in row:
                # Use '.' for empty cells (0) for cleaner display
                display_val = str(cell) if cell != 0 else "."
                row_str += f"{display_val:>{max_len}} "
            print(row_str)
        print("---------------------------------------") 



class Plant(PlatformObject):
    
    """
    A specific object type representing a single-tile plant, 
    with custom attributes.
    """

    def __init__(self, plant_id: str, name: str, species: str, water_rate: float, 
                 growth_rate: float, disease_resistance: float, 
                 sun_tolerance: str, special_property: str, soil_requirement: str):
        initial_mask = GLOBAL_GROWTH_MASKS["seedling"]
        super().__init__(obj_id=plant_id, length_tiles=1, width_tiles=1, shape_mask=initial_mask) 
        
        self.name = name
        self.species = species
        self.water_rate = water_rate
        self.life_stage = "seedling"
        self.growth_rate = growth_rate
        self.disease_resistance = disease_resistance
        self.sun_tolerance = sun_tolerance
        self.special_property = special_property
        self.soil_requirement = soil_requirement
    

    
def run_tests():
    # 1. Platform Setup
    platform_width = 10
    platform_length = 5
    platform = TilePlatform(platform_width, platform_length)
    platform.display()

    # 2. Object Initialization Tests
    print("\n--- Object Initialization Tests ---")
    
    # Test 2.1: Default solid rectangle mask (3x2)
    obj_rect = PlatformObject(obj_id="HouseA", width_tiles=3, length_tiles=2)
    print(f"Object: {obj_rect.id}, Mask: {obj_rect.shape_mask}")

    # Test 2.2: Irregular shape mask (The 'mature_tree' mask from GLOBAL_GROWTH_MASKS)
    irregular_mask = GLOBAL_GROWTH_MASKS["mature_tree"]
    obj_irregular = PlatformObject(obj_id="TreeX", width_tiles=3, length_tiles=3, shape_mask=irregular_mask)
    print(f"Object: {obj_irregular.id}, Mask: {obj_irregular.shape_mask}")

    # Test 2.3: Plant initialization (should be 1x1)
    plant_a = Plant(
        plant_id="PlantA", name="Rose", species="R. gallica", water_rate=0.5,
        growth_rate=0.1, disease_resistance=0.8, sun_tolerance="Full Sun",
        special_property="Scented", soil_requirement="Loamy"
    )
    print(f"Plant: {plant_a.id}, Dimensions: {plant_a.width_tiles}x{plant_a.length_tiles}, Stage: {plant_a.life_stage}, Mask: {plant_a.shape_mask}")
    
    # Separator
    print("\n" + "="*50)

    # 3. Placement Tests

    # Test 3.1: Successful Placement of a 3x2 rectangle (HouseA) at (1, 1)
    print("\n--- Test 3.1: Successful Placement (HouseA) ---")
    success_house = platform.place_object(start_x=1, start_y=1, obj=obj_rect)
    print(f"Placement HouseA successful: {success_house}")

    # Test 3.2: Successful Placement of a 1x1 Plant (PlantA) at (7, 4)
    print("\n--- Test 3.2: Successful Placement (PlantA) ---")
    success_plant = platform.place_object(start_x=7, start_y=4, obj=plant_a)
    print(f"Placement PlantA successful: {success_plant}")
    
    # Display the grid after placements
    platform.display()

    # Test 3.3: Boundary Check - Placement out of X-bounds (10 is platform width)
    print("\n--- Test 3.3: Boundary Check (Too far right) ---")
    obj_small = PlatformObject(obj_id="Rock", width_tiles=1, length_tiles=1)
    platform.place_object(start_x=platform_width, start_y=0, obj=obj_small)

    # Test 3.4: Boundary Check - Placement out of Y-bounds (5 is platform length)
    print("\n--- Test 3.4: Boundary Check (Too far down) ---")
    platform.place_object(start_x=0, start_y=platform_length, obj=obj_small)

    # Test 3.5: Negative Coordinate Check
    print("\n--- Test 3.5: Negative Coordinate Check ---")
    platform.place_object(start_x=-1, start_y=0, obj=obj_small)

    # Test 3.6: Collision Check - Placing a 2x1 object on top of HouseA (HouseA is at 1,1 to 3,2)
    print("\n--- Test 3.6: Collision Check (Overlapping HouseA) ---")
    obj_collision = PlatformObject(obj_id="Fence", width_tiles=2, length_tiles=1)
    # Target (2, 2) is occupied by HouseA
    platform.place_object(start_x=2, start_y=2, obj=obj_collision)

    # Test 3.7: Duplicate ID Check
    print("\n--- Test 3.7: Duplicate ID Check ---")
    platform.place_object(start_x=6, start_y=1, obj=obj_rect) # Attempt to place 'HouseA' again

    # Test 3.8: Placement that should succeed (TreeX)
    print("\n--- Test 3.8: Successful Placement (TreeX, irregular) ---")
    # TreeX is 3x3. Place at (5, 1). Occupies (5,1) to (7,3).
    success_tree = platform.place_object(start_x=5, start_y=1, obj=obj_irregular)
    print(f"Placement TreeX successful: {success_tree}")

    # Final Display
    platform.display()
    
    # 4. Retrieval Test
    print("\n--- Object Retrieval Test ---")
    retrieved_plant = platform.get_object_instance("PlantA")
    print(f"Retrieved object instance: {retrieved_plant}")
    if retrieved_plant:
        print(f"Retrieved PlantA's species: {retrieved_plant.species}")
        
    retrieved_nonexistent = platform.get_object_instance("NonExist")
    print(f"Retrieved object instance: {retrieved_nonexistent}")
    
run_tests()