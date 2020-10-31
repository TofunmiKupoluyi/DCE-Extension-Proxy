import pymongo
from mitmproxy import http
import re
class SimplifyProxy:
    def __init__(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["capstone_project"]
        self.collection = db["central"]
        self.collection.create_index("siteName", unique=True)

    def request(self, flow):
        flow.alreadyIndexed = False
        flow.initiatingUrl = None
        # Presence of initiating-url lets us know our extension is being used
        if "initiating-url" in flow.request.headers:
            # Attempt to insert, there is a unique condition so if it faily, it fails
            flow.initiatingUrl = flow.request.headers["initiating-url"]
            try: 
                self.collection.insert_one(
                    {
                        "siteName": flow.initiatingUrl, 
                        "modules" : []
                    }
                )
            except Exception:
                pass
            
            if flow.initiatingUrl != None:
                del flow.request.headers["initiating-url"]
            
            requestedUrl = flow.request.url
            siteObject = self.collection.find_one({"siteName": flow.initiatingUrl})
            if siteObject != None: 
                for module in siteObject["modules"]:
                    if module["url"] == requestedUrl:
                        flow.alreadyIndexed = True
                        flow.response = http.HTTPResponse.make(
                            module["statusCode"],
                            module["latestBody"],
                            module["responseHeaders"]
                        )

    def response(self, flow):
        
        if "access-control-allow-headers" in flow.response.headers:
            flow.response.headers["access-control-allow-headers"] = flow.response.headers["access-control-allow-headers"]
            print(flow.response.headers)
        
        # If we are at the response stage, we didn't have it in our database, so simply add it to db
        if flow.initiatingUrl and not flow.alreadyIndexed:
            # flow.response.headers["access-control-allow-origin"] = flow.initiatingUrl
            if flow.request.url == "https://st.deviantart.net/eclipse/browser-support.min.js?3":
                print(flow.response.headers)
                print(flow.response.headers["access-control-allow-origin"])
            self.collection.update_one(
                {"siteName": flow.initiatingUrl}, 
                {
                    "$push": {
                        "modules" : {
                            "url" : flow.request.url,
                            "responseHeaders": flow.response.headers,
                            "originalBody": flow.response.get_text(),
                            "latestBody": flow.response.get_text(),
                            "statusCode": flow.response.status_code
                        }
                    }
                }
            )
            
                

addons = [
    SimplifyProxy()
]