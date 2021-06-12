from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# noinspection PyUnresolvedReferences
from little_brother.persistence import persistence_base, persistent_user_2_device, persistent_device, \
    persistent_process_info, \
    persistent_daily_user_status, persistent_user, persistent_rule_set, persistent_rule_override, \
    persistent_time_extension, \
    persistent_admin_event, persistence

# *************************************************************************************************
# IMPORTANT
# *************************************************************************************************
# In order for the alembic auto generation mechanism to be able to detect the current model
# ALL modules having a reference to the declarative_base() have to be imported!
# See https://stackoverflow.com/questions/15660676/alembic-autogenerate-producing-empty-migration
# *************************************************************************************************

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

target_metadata = persistence_base.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config_section = config.get_section(config.config_ini_section)

    if config.cmd_opts.x is not None:
        config_section['sqlalchemy.url'] = config.cmd_opts.x[0]

    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
