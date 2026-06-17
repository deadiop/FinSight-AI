from sqlalchemy import text
from backend.database.db import engine
from backend.models.transaction import Base

def run_migration():
    print("Starting migration...")
    
    # 1. Create tables that do not exist (like 'users')
    Base.metadata.create_all(bind=engine)
    print("Checked and created missing tables (like 'users').")

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 2. Check if user_id column exists on transactions table
            result = conn.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'transactions' AND column_name = 'user_id';
                """)
            ).fetchone()
            
            if not result:
                print("Adding 'user_id' column to 'transactions'...")
                conn.execute(
                    text("""
                    ALTER TABLE transactions 
                    ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
                    """)
                )
                print("Column 'user_id' added.")
            else:
                print("Column 'user_id' already exists.")

            # 3. Find and drop the old unique constraint on (date, description, amount)
            # Find any unique constraints on the transactions table
            constraints = conn.execute(
                text("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = 'transactions'::regclass AND contype = 'u';
                """)
            ).fetchall()
            
            constraint_names = [c[0] for c in constraints]
            print(f"Existing unique constraints: {constraint_names}")
            
            # Drop constraints that do not match the new one
            for name in constraint_names:
                if name != 'uix_date_desc_amount_user':
                    print(f"Dropping old constraint '{name}'...")
                    conn.execute(text(f"ALTER TABLE transactions DROP CONSTRAINT {name};"))
            
            # 4. Add the new constraint if it doesn't exist
            if 'uix_date_desc_amount_user' not in constraint_names:
                print("Adding new unique constraint 'uix_date_desc_amount_user'...")
                conn.execute(
                    text("""
                    ALTER TABLE transactions 
                    ADD CONSTRAINT uix_date_desc_amount_user UNIQUE (date, description, amount, user_id);
                    """)
                )
                print("Unique constraint 'uix_date_desc_amount_user' added.")
            else:
                print("Unique constraint 'uix_date_desc_amount_user' already exists.")
                
            trans.commit()
            print("Migration completed successfully!")
        except Exception as e:
            trans.rollback()
            print(f"Migration failed: {e}")
            raise e

if __name__ == "__main__":
    run_migration()
