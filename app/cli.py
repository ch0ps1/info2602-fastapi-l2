import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select, or_
from sqlalchemy.exc import IntegrityError
from typing import Annotated

cli = typer.Typer()

@cli.command()
def initialize():
    """Initialize the database with some data. Example usage: `python cli.py initialize`"""
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")


@cli.command()
def get_user(username:Annotated[str, typer.Argument(help="The username of the user to retrieve")]):
    """Get a user by their username. Example usage: `python cli.py get-user bob`
    """
    # The code for task 5.1 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found')
            return
        print(user)

@cli.command()
def get_all_users():
    """Get all users in the database. Example usage: `python cli.py get-all-users`"""
    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print('No users found')
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: Annotated[str, typer.Argument(help="The Username of the user who's email is to be changed.")], new_email:Annotated[str, typer.Argument(help="The new email address to set for the user.")]):
    """
    Change a user's email address. Example usage: `python cli.py change-email bob
    """
    # The code for task 6 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"updated {user.username}'s email to {user.email}.")
        
@cli.command()
def create_user(username: Annotated[str, typer.Argument(help="Username to be set for new user.")], email:Annotated[str, typer.Argument(help="Email to be set for new user")], password: Annotated[str, typer.Argument(help="Password to be set for new user.")]):
    """Create a new user. Example usage: `python cli.py create-user bob"""
    # The code for task 7 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: Annotated[str, typer.Argument(help="The username of the user to delete")]):
    """Delete a user by their username. Example usage: `python cli.py delete-user bob`"""
    # The code for task 8 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command()
def partial_match(search_term: Annotated[str, typer.Argument(help="The search term to use for finding users")]):
    """Search for users by partial match on username or email. Example usage: `python cli.py partial-match bo`"""
    with get_session() as db:
        
        pattern = f"%{search_term}%"
        
        users = db.exec(select(User).where(or_(User.username.contains(search_term), User.email.contains(search_term)))).all()
        if not users:
            print(f'No users found matching "{search_term}"')
        else:
            for user in users:
                print(user)

@cli.command()
def add_users():
    """Add multiple users to the database for testing pagination. Example usage: `python cli.py add-users`"""
    user_1 = User('alice','alicemail.com', 'alicepass')
    user_2 = User('bill', 'billmail.com', 'billpass')
    user_3 = User('cathy', 'cathymail.com','cathypass')
    user_4 = User('dave','davemail.com', 'davepass')
    user_5 = User('eve', 'evemail.com', 'evepass')
    user_6 = User('frank','frankmail.com','frankpass')
    user_7 = User('grace', 'gracemail.com', 'gracepass')
    user_8 = User('heidi', 'heidimail.com', 'heidipass')
    user_9 = User('ivan','ivanmail.com', 'ivanpass')
    user_10 = User('judy','judymail.com', 'judypass')
    with get_session() as db:
        db.add_all([user_1, user_2, user_3, user_4, user_5, user_6, user_7, user_8, user_9, user_10])
        db.commit()


@cli.command()
def paginated_users(offset: Annotated[int, typer.Argument(help="Offset of paginated list")] = 0 , limit: Annotated[int, typer.Argument(help="Limit of the paginated list")] = 10):
    """List users in a paginated fashion. Example usage: `python cli.py paginated-users 0 5`"""
    with get_session() as db:
        
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print(f'No users found for page {offset} with page size {limit}')
        else:
            for user in users:
                print(user)




if __name__ == "__main__":
    cli()