import re

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError


DATABASE_URL = (
    "postgresql+psycopg2://admin:admin123@localhost:5432/ecommerce-analytics-dashboard"
)

SQL_IDENTIFIER_REGEX = r"^[a-zA-Z_][a-zA-Z0-9_]*$"


def get_engine() -> Engine:
    return create_engine(DATABASE_URL)


def raise_error(message: str):
    return (_ for _ in ()).throw(ValueError(message))


def validate_identifier(identifier: str) -> None:
    re.match(SQL_IDENTIFIER_REGEX, identifier) or raise_error(
        f"Invalid SQL identifier: '{identifier}'"
    )


def validate_column_exists(
    connection: Connection,
    table_name: str,
    column_name: str
) -> None:

    column_exists = connection.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = :table_name
                AND column_name = :column_name
            );
        """),
        {
            "table_name": table_name,
            "column_name": column_name
        }
    ).scalar()

    column_exists or raise_error(
        f"Column '{column_name}' does not exist "
        f"in table '{table_name}'."
    )


def validate_no_nulls(
    connection: Connection,
    table_name: str,
    column_name: str
) -> None:

    null_count = connection.execute(
        text(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE {column_name} IS NULL;
        """)
    ).scalar()

    (null_count == 0) or raise_error(
        f"Column '{column_name}' contains NULL values."
    )


def validate_no_duplicates(
    connection: Connection,
    table_name: str,
    column_name: str
) -> None:

    duplicated_count = connection.execute(
        text(f"""
            SELECT COUNT(*)
            FROM (
                SELECT {column_name}
                FROM {table_name}
                GROUP BY {column_name}
                HAVING COUNT(*) > 1
            ) duplicated_rows;
        """)
    ).scalar()

    (duplicated_count == 0) or raise_error(
        f"Column '{column_name}' contains duplicated values."
    )


def validate_no_orphans(
    connection: Connection,
    source_table: str,
    source_column: str,
    target_table: str,
    target_column: str
) -> None:

    orphan_count = connection.execute(
        text(f"""
            SELECT COUNT(*)
            FROM {source_table} s
            LEFT JOIN {target_table} t
                ON s.{source_column} = t.{target_column}
            WHERE t.{target_column} IS NULL;
        """)
    ).scalar()

    (orphan_count == 0) or raise_error(
        f"Orphan records found in "
        f"'{source_table}({source_column})'."
    )


def assign_primary_key(
    table_name: str,
    column_name: str
) -> None:

    try:

        identifiers = [table_name, column_name]
        list(map(validate_identifier, identifiers))

        engine = get_engine()

        with engine.begin() as connection:

            validate_column_exists(
                connection,
                table_name,
                column_name
            )

            validate_no_nulls(
                connection,
                table_name,
                column_name
            )

            validate_no_duplicates(
                connection,
                table_name,
                column_name
            )

            connection.execute(
                text(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT pk_{table_name}
                    PRIMARY KEY ({column_name});
                """)
            )

            print(
                f"Primary key successfully created on "
                f"'{table_name}({column_name})'."
            )

    except SQLAlchemyError as error:
        raise RuntimeError(
            f"Database error: {error}"
        ) from error


def add_relation(
    source_table: str,
    source_column: str,
    target_table: str,
    target_column: str
) -> None:

    try:

        identifiers = [
            source_table,
            source_column,
            target_table,
            target_column
        ]

        list(map(validate_identifier, identifiers))

        engine = get_engine()

        with engine.begin() as connection:

            validate_column_exists(
                connection,
                source_table,
                source_column
            )

            validate_column_exists(
                connection,
                target_table,
                target_column
            )

            validate_no_orphans(
                connection,
                source_table,
                source_column,
                target_table,
                target_column
            )

            connection.execute(
                text(f"""
                    ALTER TABLE {source_table}
                    ADD CONSTRAINT fk_{source_table}_{target_table}
                    FOREIGN KEY ({source_column})
                    REFERENCES {target_table} ({target_column});
                """)
            )

            print(
                f"Foreign key successfully created between "
                f"'{source_table}({source_column})' and "
                f"'{target_table}({target_column})'."
            )

    except SQLAlchemyError as error:
        raise RuntimeError(
            f"Database error: {error}"
        ) from error