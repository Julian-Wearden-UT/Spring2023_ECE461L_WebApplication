# Documentation for Flask Endpoints

This file contains endpoints for accessing and modifying data related to hardware sets.

## Endpoints

### `GET /get_hardware_set_data/<int:whichSet>`

Returns the capacity, availability, and description of a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.

**Returns**

- A JSON object containing the following fields:
  - `Capacity` (number): The capacity of the hardware set.
  - `Availability` (number): The number of available hardware items in the set.
  - `Description` (string): A description of the hardware set.

### `GET /get_capacity/<int:whichSet>`

Returns the capacity of a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.

**Returns**

- A JSON object containing the following field:
  - `Capacity` (number): The capacity of the hardware set.

### `GET /get_availability/<int:whichSet>`

Returns the availability of a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.

**Returns**

- A JSON object containing the following field:
  - `Availability` (number): The number of available hardware items in the set.

### `GET /get_description/<int:whichSet>`

Returns the description of a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.

**Returns**

- A JSON object containing the following field:
  - `Description` (string): A description of the hardware set.

### `GET /check_in/<int:whichSet>/<int:amount>`

Checks in hardware to a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.
- `amount` (int): The number of hardware items to check in.

**Returns**

- A JSON object containing the following field:
  - `Status` (int or string): 0 if the check-in was successful, or an error message if there was not enough room to check in all hardware.

### `GET /check_out/<int:whichSet>/<int:amount>`

Checks out hardware from a hardware set.

**Parameters**

- `whichSet` (int): Either 1 or 2, depending on which hardware set to access.
- `amount` (int): The number of hardware items to check out.

**Returns**

- A JSON object containing the following field:
  - `Status` (int or string): 0 if the check-out was successful, or an error message if there was not enough hardware to check out.
