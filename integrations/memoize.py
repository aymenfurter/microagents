import hashlib
import json
import sqlite3

## retrieved from https://www.kevinkatz.io/posts/memoize-to-sqlite

def memoize_to_sqlite(func_name:str, filename: str = "cache.db"):
    """
    Memoization decorator that caches the output of a method in a SQLite
    database.
    """
    db_conn = sqlite3.connect(filename)
    print("opening database")
    db_conn.execute(
        "CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, result TEXT)"
    )

    db_conn.execute(
        "CREATE INDEX IF NOT EXISTS cache_ndx on cache(hash)"
    )

    def memoize(func):
        def wrapped(*args, **kwargs):
            # Compute the hash of the <function name>:<argument>
            #xs = f"{func.__name__}:{repr(tuple(args))}".encode("utf-8")
            xs = f"{func_name}:{repr(tuple(args[1:]))}:{repr(kwargs)}".encode("utf-8")
            print(xs)
            arg_hash = hashlib.sha256(xs).hexdigest()

            # Check if the result is already cached
            cursor = db_conn.cursor()
            cursor.execute(
                "SELECT result FROM cache WHERE hash = ?", (arg_hash,)
            )
            row = cursor.fetchone()
            if row is not None:
                print(f"Cached result found for {arg_hash}. Returning it.")
                if func_name == "chat_completion":
                   print(json.loads(row[0]))
                return json.loads(row[0])

            # Compute the result and cache it
            print("getting results from %s" % func_name)
            result = func(*args, **kwargs)
            if func_name == "chat_completion":
               print(result)
            cursor.execute(
                "INSERT INTO cache (hash, result) VALUES (?, ?)",
                (arg_hash, json.dumps(result))
            )
            db_conn.commit()

            return result

        return wrapped

    return memoize
