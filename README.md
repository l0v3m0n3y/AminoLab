# AminoLab
Async library for aminoapps.com
# example
#Login
```python3
import AminoLab,asyncio
async def main():
	client = AminoLab.AminoLab()
	email = input("Email >> ")
	password = input("Password >> ")
	await client.auth(email=email, password=password)
asyncio.get_event_loop().run_until_complete(main())
```
