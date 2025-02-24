import pymongo

maxSevSelDelay = 1000  


def connect_to_db():
    try:
        client = pymongo.MongoClient(
            "mongodb://admin:password@mongodb:27017",
            serverSelectionTimeoutMS=maxSevSelDelay
        )
        
        client.server_info()
        db = client["stream-sense"]
        print("MongoDB connection successful!")
        return db


    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Error connecting to MongoDB:", err)
