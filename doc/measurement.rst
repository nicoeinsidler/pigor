The Measurement Class
=====================

Flow at Startup
---------------

1. read the data
2. detect measurement type
3. read position file if a position file exists
4. clean up and description gathering
5. select columns for plotting

.. mermaid::

    graph TB
    init["__init__()"] --> read_data["read_data()"]
    init -- "if type_of_measurement != default"  --> detect_measurement_type["detect_measurement_type()"]
    init -- "if type_of_measurement == POL"  --> read_pos_file["read_pos_file()"]
    init --> clean_data["clean_data()"]
    init --> select_columns["select_columns()"]
    subgraph 5.
      select_columns
    end
    subgraph 4.
      clean_data
    end
    subgraph 3.
      read_pos_file
    end
    subgraph 2.
      detect_measurement_type --> measurement_type["measurement_type()"]
    end
    subgraph 1.
      read_data
    end


Methods
-------

.. automodule:: measurement
    :members: