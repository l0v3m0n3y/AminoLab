# Library In Development created by l0v3m0n3y
# I have not tested some functions.
import asyncio,aiohttp,base64,random,time
from functools import reduce
from time import time
from typing import BinaryIO, Union
from .utils import headers, objects, exception
from json import dumps,loads

class AminoLab():
    def __init__(self):
        self.api = "https://aminoapps.com/api"
        self.api_p = "https://service.aminoapps.com/api/v1"
        self.headers = headers.Headers().headers
        self.headers_v2 = headers.Headers().headers_v2
        self.session=aiohttp.ClientSession()
        self.user_Id = None
        self.sid = None
    def __del__(self):
             try:
             	loop = asyncio.get_event_loop()
             	loop.create_task(self._close_session())
             except RuntimeError:
             	loop = asyncio.new_event_loop()
             	loop.run_until_complete(self._close_session())
    async def _close_session(self):
    	if not self.session.closed: await self.session.close()
    async def auth_sid(self,sid):
    	data = loads(base64.b64decode(reduce(lambda a, e: a.replace(*e), ("-+","_/"),sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())
    	self.sid = sid
    	self.user_Id =data["2"]
    	headers.sid = self.sid
    	headers.user_Id = self.user_Id
    	self.headers = headers.Headers(sid=self.sid).headers
    	self.headers_v2 = headers.Headers(sid=self.sid).headers_v2
    async def auth(self, email: str = None, phone: str = None, password: str = None,secret:str=None):
        data ={
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": headers.generate_deviceId(),
			"clientType": 100,
			"action": "normal",
			"timestamp": int(time() * 1000)}
        if email:
            data["email"] = email
        elif phone:
            data["phoneNumber"] = phone
        async with self.session.post(f"{self.api_p}/g/s/auth/login", json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
            try:
            	json=await request.json()
            	self.sid = json["sid"]
            	self.user_Id = json["account"]["uid"]
            	headers.sid = self.sid
            	headers.user_Id = self.user_Id
            	self.headers = headers.Headers(sid=self.sid).headers
            	self.headers_v2 = headers.Headers(sid=self.sid).headers_v2
            	return await request.json()
            except BaseException:
            	return exception.CheckExceptions(await request.json())

    # logout
    async def logout(self):
        data={"deviceID":headers.generate_deviceId(),"clientType": 100, "timestamp": int(time() * 1000)}
        async with self.session.post(f"{self.api_p}/g/s/auth/logout", json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as requests:
        	self.sid = None
        	self.user_Id = None
        	self.headers = None
        	self.headers_v2 =None
        	return response.status_code

    # get public chats list
    async def get_public_chat_threads(self, ndc_Id, type: str = "recommended", start: int = 0, size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/{patch}/chat/thread?type=public-all&filterType={type}&start={start}&size={size}",headers=self.headers_v2) as requests:
        	json=await requests.json()
        	return objects.ChatThreads(json["threadList"]).ChatThreads

    # get joined chats list
    async def my_chat_threads(self, ndc_Id, start: int = 0, size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/{patch}/chat/thread?type=joined-me&start={start}&size={size}",headers=self.headers_v2) as requests:
        	json=await requests.json()
        	return objects.ChatThreads(json["threadList"]).ChatThreads

    #
    async def send_message(self,ndc_Id,thread_Id,message: str = None,message_type: int = 0,stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
    	data = {
			"type": message_type,
			"content": message,
			"clientRefId": int(time() / 10 % 1000000000),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImage
			},
			"extensions": {"mentionedArray": mentions},
			"timestamp": int(timestamp() * 1000)
		}
    	if stickerId:
    		data["content"] = None
    		data["stickerId"] = stickerId
    		data["type"] = 3
    	if ndc_Id:patch=f"x{ndc_Id}/s"
    	else:patch="g/s"
    	async with self.session.post(f"{self.api_p}/{patch}/chat/thread/{thread_Id}/message",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
    		return await request.json()

    # get user information
    async def get_user_info(self, user_Id: str,ndc_Id:int=None):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/{patch}/user-profile/{user_Id}",headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.UserInfo(json["userProfile"]).UserInfo
    # comment
    #
    async def submit_comment(self,ndc_Id,message,user_Id: str = None,blog_Id: str = None,wiki_Id: str = None):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        data = {"content": message,"stickerId": None,"type": 0,"timestamp": int(time() * 1000)}
        if user_Id:
            data["eventSource"] = "UserProfileView"
            async with self.session.post(f"{self.api_p}/{patch}/user-profile/{user_Id}/g-comment",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
            	return await request.json()

        elif blog_Id:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            
            async with self.session.post(f"{self.api_p}/{patch}/blog/{blog_Id}/g-comment",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
            	return await request.json()

        elif wiki_Id:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            
            async with self.session.post(f"{self.api_p}/{patch}/item/{wiki_Id}/g-comment",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
            	return await request.json()

    # get supported languages list
    async def get_supported_languages(self):
        async with self.session.get(f"{self.api_p}/g/s/community-collection/supported-languages",headers=self.headers_v2) as request:
            	return await request.json()
    async def join_thread(self, ndc_Id, thread_Id):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.post(f"{self.api_p}/{patch}/chat/thread/{thread_Id}/member/{self.user_Id}",headers=self.headers_v2) as request:
        	return await request.json()
    async def leave_thread(self, ndc_Id, thread_Id):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.post(f"{self.api_p}/{patch}/chat/thread/{thread_Id}/member/{self.user_Id}",headers=self.headers_v2) as request:
        	return await request.json()

    # get online users
    async def get_online_members(self, ndc_Id: str, start: int = 0, size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/x{ndc_Id}/s/live-layer?topic=ndtopic:x{ndc_Id}:online-members&start={start}&size={size}",headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.MembersList(json["userProfileList"]).MembersList

    # get recent users
    async def get_recent_members(self, ndc_Id: str, start: int = 0, size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/x{ndc_Id}/s/user-profile?type=recent&start={start}&size={size}",headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.MembersList(json["userProfileList"]).MembersList

    # get banned users
    async def get_banned_members(self, ndc_Id: str, start: int = 0, size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(f"{self.api_p}/x{ndc_Id}/s/user-profile?type=banned&start={start}&size={size}",headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.MembersList(json["userProfileList"]).MembersList

    # get community curators
    async def get_curators_list(self, ndc_Id: str):
        async with self.session.get(f"{self.api_p}/x{ndc_Id}/s/user-profile?type=curators",headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.MembersList(json["userProfileList"]).MembersList

    # get community leaders
    async def get_leaders_list(self, ndc_Id: str):
        async with self.session.get(
            f"{self.api_p}/x{ndc_Id}/s/user-profile?type=leaders",
            headers=self.headers_v2) as request:
        	json=await request.json()
        	return objects.MembersList(json["userProfileList"]).MembersList

    # get public communities list, languages - ru = Russia, en = English
    async def get_public_communities(self, language: str, size: int = 25):
        async with self.session.get(
            f"{self.api_p}/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t",
            headers=self.headers_v2) as request:
            	json=await request.json()
            	return objects.CommunityList(json["communityList"]).CommunityList

    # get joined communities list
    async def my_communities(self):
        async with self.session.get(
            f"{self.api_p}/g/s/community/joined",
            headers=self.headers_v2) as request:
            	json=await request.json()
            	return objects.CommunityList(json["communityList"]).CommunityList

    #
    async def follow_user(self, ndc_Id, user_Id: str):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.post(
            f"{self.api_p}/{patch}/user-profile/{user_Id}/member",
            json=data,headers=self.headers_v2) as request:
            	return await request.json()

    #
    async def unfollow_user(self, ndc_Id, user_Id: str):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.post(
            f"{self.api_p}/{patch}/user-profile/{user_Id}/member/{self.user_Id}",
            json=data,
            headers=self.headers_v2) as request:
            	return await request.json()

    #
    async def vote(self, ndc_Id, blog_Id: str = None, wiki_Id: str = None):
        data = {
            "value": 4,
            "timestamp": int(time() * 1000)
        }

        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        if blog_Id:
            if isinstance(blog_Id, str):
                data["eventSource"] = "UserProfileView"
                async with self.session.post(f"{self.api_p}/{patch}/blog/{blog_Id}/g-vote?cv=1.2",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
                	return await request.json()

            elif isinstance(blog_Id, list):
                data["targetIdList"] = blog_Id
                async with self.session.post(f"{self.api_p}/{patch}/feed/g-vote",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
                	return await request.json()
            else: pass

        elif wiki_Id:
            data["eventSource"] = "PostDetailView"
            async with self.session.post(f"{self.api_p}/{patch}/item/{wiki_Id}/g-vote?cv=1.2",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
            	return await request.json()
    #
    async def unvote(self, ndc_Id, blog_Id: str = None, wiki_Id: str = None):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        if blog_Id:
        	async with self.session.delete(f"{self.api_p}/g/s/blog/{blog_Id}/g-vote?eventSource=UserProfileView", headers=self.headers_v2) as request:
        		return await request.json()
        elif wiki_Id:
        	async with self.session.delete(f"{self.api_p}/g/s/item/{wiki_Id}/g-vote?eventSource=PostDetailView", headers=self.headers_v2) as request:
        		return await request.json()

    # get community blogs list
    async def get_recent_blogs(self, ndc_Id: str, start: int = 0, size: int = 10):
        async with self.session.get(
            f"{self.api_p}/x{ndc_Id}/s/feed/blog-all?pagingType=t&start={start}&size={size}",
            headers=self.headers_v2) as request:
            	json=await request.json()
            	return objects.BlogsList(json["blogList"]).BlogsList

    # 
    async def join_community(self, ndc_Id: str):
        data = {"timestamp": int(time() * 1000)}
        async with self.session.post(f"{self.api_p}/x{ndc_Id}/s/community/join",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    async def leave_community(self, ndc_Id: str):
        async with self.session.post(
            f"{self.api}/x{ndc_Id}/s/community/leave",headers=self.headers_v2) as request:
        	return await request.json()

    async def request_join_community(self, ndc_Id, message: str = None):
        data = {"message": message, "timestamp": int(time() * 1000)}
        async with self.session.post(
            f"{self.api_p}/x{ndc_Id}/s/community/membership-request",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    #
    async def report(
            self,
            ndc_Id,
            reason: str,
            flag_type: int,
            user_Id: str = None,
            blog_Id: str = None,
            wiki_Id: str = None,
            thread_Id: str = None):
        data = {
            "flagType": flagType,
            "message": reason,
            "timestamp": int(time() * 1000)
        }
        if user_Id:
            data["objectId"] = user_Id
            data["objectType"] = 0
        elif blog_Id:
            data["objectId"] = blog_Id
            data["objectType"] = 1
        elif wiki_Id:
            data["objectId"] = wiki_Id
            data["objectType"] = 2
        elif thread_Id:
            data["objectId"] = thread_Id
            data["objectType"] = 12
        async with self.session.post(f"{self.api_p}/flag",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # get websocket url
    async def get_web_socket_url(self):
        async with self.session.get(
            f"{self.api}/chat/web-socket-url",
            headers=self.headers) as request:
            	return await request.json()

    # get link information
    async def get_from_link(self, link: str):
        async with self.session.get(
            f"{self.api_p}/g/s/link-resolution?q={link}",
            headers=self.headers_v2) as request:
            	json=await request.json()
            	return objects.FromLink(json["linkInfoV2"]).FromLink

    # get blocked and blocker full list
    async def block_full_list(self):
        async with self.session.get(
            f"{self.api}/block/full-list",
            headers=self.headers) as request:
            	return await request.json()

    # 
    async def create_chat_thread(
            self,
            ndc_Id,
            user_Id: str,
            message: str,
            title: str = None,
            type: int = 0):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        if isinstance(userId, str): userIds = [user_Id]
        elif isinstance(userId, list): userIds = user_Id
        data = {
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(timestamp() * 1000)
        }
        if title:
            data["title"] = title
        async with self.session.post(
            f"{self.api}/{patch}/chat/thread",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # thread check, useless function
    async def thread_check(self, ndc_Id):
        data = {"ndcId": f"x{ndc_Id}"}
        async with self.session.get(
            f"{self.api}/thread-check",
            params=data,
            headers=self.headers) as request:
        	return await request.json()

    # get live layer
    async def get_live_layer(self, ndc_Id):
        async with self.session.get(
            f"{self.api}/x{ndc_Id}/s/live-layer/homepage?v=2",
            headers=self.headers) as request:
        	return await request.json()

    #
    async def link_translation(
            self,
            ndc_Id,
            user_Id: str = None,
            blog_Id: str = None,
            wiki_Id: str = None,
            thread_Id: str = None):
        data = {"targetCode": 1,"timestamp": int(time() * 1000)}
        if user_Id:
            data["objectId"] = user_Id
            data["objectType"] = 0
        elif blog_Id:
            data["objectId"] = blog_Id
            data["objectType"] = 1
        elif wiki_Id:
            data["objectId"] = wiki_Id
            data["objectType"] = 2
        elif thread_Id:
            data["objectId"] = thread_Id
            data["objectType"] = 12
        if ndc_Id:
        	async with self.session.post(f"{self.api}/g/s-x{ndc_Id}/link-resolution",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        		return await request.json()
        else:
        	async with self.session.post(f"{self.api}/g/s/link-resolution",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        		return await request.json()

    # get chat bubbles list
    async def get_bubbles_list(self):
        async with self.session.get(
            f"{self.api_p}/g/s/chat/chat-bubble",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get chat bubbles templates list
    async def get_bubbles_templates_list(self):
        async with self.session.get(
            f"{self.api_p}/g/s/chat/chat-bubble/templates",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get avatar frames list
    async def get_avatar_frames_list(self, start: int = 0, size: int = 10):
        async with self.session.get(
            f"{self.api_p}/g/s/avatar-frame?start={start}&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()
    # edit profile
    async def edit_profile(
            self,
            ndc_Id,
            nickname: str = None,
            content: str = None,
            icon: str = None,
            background_color: str = None):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        data = {}
        if nickname:
            data["nickname"] = nickname
        if content:
            data["content"] = content
        if icon:
            data["icon"] = icon
        if background_color:
            data["extensions"] = {
                "style": {
                    "backgroundColor": background_color}}
        async with self.session.post(f"{self.api_p}/{patch}/user-profile/{self.user_Id}",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # delete chat
    async def delete_thread(self, ndc_Id, thread_Id: str):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.delete(f"{self.api_p}/{patch}/chat/thread/{thread_Id}",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get wallet coin history info
    async def wallet_coin_history(self, start: int = 0, size: int = 10):
        async with self.session.get(
            f"{self.api_p}/g/s/wallet/coin/history?start={start}&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()

    # edit thread(chat)
    async def edit_thread(
            self,
            ndc_Id,
            thread_Id: str,
            title: str = None,
            content: str = None,
            fans_only: bool = None):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if fans_only:
            data["extensions"] = {"fansOnly": fans_only}
        async with self.session.post(
            f"{self.api_p}/{patch}/chat/thread/{thread_Id}",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # get account info
    async def get_account_info(self):
        async with self.session.get(
            f"{self.api_p}/g/s/account",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get user followers
    async def get_user_followers(
            self,
            ndc_Id,
            user_Id: str,
            start: int = 0,
            size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(
            f"{self.api_p}/{patch}/user-profile/{user_Id}/member?start={start}&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()
    # get user following
    async def get_user_following(
            self,
            ndc_Id,
            user_Id: str,
            start: int = 0,
            size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(
            f"{self.api_p}/{patch}/user-profile/{user_Id}/joined?start={start}&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()

    # search user or users in community
    async def search_users(
            self,
            ndc_Id,
            nickname: str,
            start: int = 0,
            size: int = 10):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(
            f"{self.api_p}/{patch}/user-profile?type=name&q={nickname}&start={start}&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get blog categories
    async def blog_category(self, ndc_Id: str):
        async with self.session.get(
            f"{self.api}/get-blog-category?ndcId={ndc_Id}",
            headers=self.headers) as request:
        	return await request.json()

    # get community info
    async def community_info(self, ndc_Id: str):
        async with self.session.get(
            f"{self.api_p}/g/s-x{ndc_Id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount",
            headers=self.headers_v2) as request:
        	return await request.json()

    #
    async def create_blog(
            self,
            ndc_Id,
            title: str,
            content: str = None,
            categories_list: list = None,
            extensions: dict = None,
            fans_only: bool = False,
            type: int = 0):
        media_list = []
        data = {
            "address": None,
            "content": content,
            "title": title,
            "mediaList": media_list,
            "extensions": extensions,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(time() * 1000)
        }

        if fans_only: data["extensions"] = {"fansOnly": fans_only}
        if categories_list: data["taggedBlogCategoryIdList"] = categories_list
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.post(
            f"{self.api_p}/{patch}/blog",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    #
    async def delete_blog(self, ndc_Id: str, blog_Id: str):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.delete(f"{self.api_p}/{patch}/blog/{blog_Id}",headers=self.headers_v2) as request:
        	return await request.json()

    # get members(users) in chat
    async def members_in_thread(
            self,
            ndc_Id: str,
            thread_Id: str,
            type: str = "default",
            start: int = 0,
            size: int = 10):
        data = {
            "ndcId": f"x{ndc_Id}",
            "threadId": thread_Id,
            "type": type,
            "start": start,
            "size": size
        }
        async with self.session.get(
            f"{self.api}/members-in-thread",
            params=data,
            headers=self.headers) as request:
        	return await request.json()

    # get user visitors
    async def get_user_visitors(self, ndc_Id: str, user_Id: str):
        async with self.session.get(
            f"{self.api_p}/x{ndc_Id}/s/user-profile/{user_Id}/visitors",
            headers=self.headers_v2) as request:
        	return await request.json()

    # configure account settings
    # gender: 1 = male, 2 = female, 255 = non-binary
    async def configure_account(self, age: int, gender: int):
        data = {"age": age, "gender": gender,"timestamp": int(time() * 1000)}
        async with self.session.post(
            f"{self.api_p}/g/s/persona/profile/basic",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # get chat messages
    async def get_thread_messages(self, ndc_Id: str, thread_Id: str, size: int = 10):
        async with self.session.get(
            f"{self.api_p}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?v=2&pagingType=t&size={size}",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get chat messages v2
    async def chat_thread_messages(
            self,
            ndc_Id: str,
            thread_Id: str,
            size: int = 10):
        data = {"ndcId": f"x{ndc_Id}", "threadId": thread_Id, "size": size}
        async with self.session.get(f"{self.api}/chat-thread-messages",params=data,
headers=self.headers) as request:
        	return await request.json()

    async def set_activity_status(self, ndc_Id: str, status: int = 1):
        data = {"onlineStatus": status, "duration": 86400,"timestamp": int(time() * 1000)}
        async with self.session.post(
            f"{self.api_p}/x{ndc_Id}/s/user-profile/{self.user_Id}/online-status",
            json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # watch ad and get 2-3 coins.
    async def watch_ad(self):
        async with self.session.post(
            f"{self.api_p}/g/s/wallet/ads/video/start",
            headers=self.headers_v2)as request:
        	return await request.json()
    # get thread(chat)
    async def get_thread(self, ndc_Id: str, thread_Id: str):
        if ndc_Id:patch=f"x{ndc_Id}/s"
        else:patch="g/s"
        async with self.session.get(
            f"{self.api_p}/{patch}/chat/thread/{thread_Id}",
            headers=self.headers_v2)as request:
        	return await request.json()

    # check in
    async def check_In(self, ndc_Id: str):
        data = {"timezone": -int(time.timezone()) // 1000}
        async with self.session.post(
            f"{self.api_p}/x{ndc_Id}/s/check-in",
            json=data,
            headers=self.headers_v2) as request:
        	return await request.json()

    # claim new user coupon
    async def claim_new_user_coupon(self):
        async with self.session.post(
            f"{self.api_p}/g/s/coupon/new-user-coupon/claim",
            headers=self.headers_v2) as request:
        	return await request.json()

    # get blog votes
    async def get_blog_votes(self, ndc_Id: str, blog_Id: str):
        async with self.session.get(
            f"{self.api}/x{ndc_Id}/blog/{blog_Id}/votes",
            headers=self.headers) as request:
        	return await request.json()

    #
    async def poll_option(self, ndc_Id: str, blog_Id: str, option_Id: str):
        data={
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(time() * 1000)
        }
        async with self.session.post(
            f"{self.api_p}/x{ndc_Id}/s/blog/{blog_Id}/poll/option/{option_Id}/vote",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    # search community
    async def search_community(self, title: str, start: int = 0, size: int = 10):
        data = {"q": title, "start": start, "size": size,"timestamp": int(time() * 1000)}
        async with self.session.post(f"{self.api_p}/g/s/community/search?q={title}&start={start}&size={size}",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    #
    async def register(
            self,
            email: str,
            password: str,
            nickname: str,
            verification_code: str):
        data = {
            "secret": f"0 {password}",
            "deviceID": headers.generate_deviceId(),
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "validationContext": {
                "data": {
                    "code": verification_code
                },
                "type": 1,
                "identity": email
            },
            "type": 1,
            "identity": email,
            "timestamp": int(time() * 1000)
        }
        async with self.session.post(
            f"{self.api}/g/s/auth/register",
            json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()
    # request security validation(request verify code)
    async def request_security_validation(
            self,
            email: str,
            reset_password: bool = False):
        data = {
            "identity": email,
            "type": 1,
            "deviceID": headers.generate_deviceId()
            
        }
        if reset_password is True:
            data["level"] = 2
            data["purpose"] = "reset-password"
        async with self.session.post(
            f"{self.api_p}/g/s/auth/request-security-validation",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()

    #
    async def check_security_validation(self, email: str, verification_code: str):
        data = {
            "validationContext": {
                "type": 1,
                "identity": email,
                "data": {"code": verification_code}},
            "deviceID": headers.generate_deviceId(),
            "timestamp": int(time() * 1000)
        }
        async with self.session.post(
            f"{self.api_p}/g/s/auth/check-security-validation",json=data,headers=headers.Headers(data=dumps(data)).headers_v2) as request:
        	return await request.json()
