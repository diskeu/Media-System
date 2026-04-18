A lightweight Reddit-like system that avoids pulling in thousands of external dependencies while remaining fully controllable.

Most backend systems rely on large stacks: a full-featured API framework like Django, complex ORM layers such as SQLAlchemy, and many additional abstractions. This project takes a different approach by intentionally minimizing external dependencies and keeping full control over the system architecture.

It uses FastAPI for routing, chosen for its high performance and relatively minimal footprint compared to frameworks like Django. For database access, it relies on the MySQL Connector, allowing direct and explicit control over SQL queries. While raw queries can be time-consuming to write, the project includes a small abstraction layer to simplify common operations without hiding the underlying SQL logic.

Additionally, a lightweight ORM layer is provided. It enables inserting and managing database entries using simple Python classes, while still avoiding heavy external ORM libraries.

The project is currently not finished, but the core foundation and system architecture are already in place.
