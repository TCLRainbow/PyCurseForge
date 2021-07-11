# PyCurseForge

CurseForge API wrapper using `aiohttp`  
Minimum Python version: `3.6` (f-strings)

[Endpoint documentation](https://twitchappapifork.docs.apiary.io)

# Table of Contents  
[Addons](#addon)  

<a name="addon"></a>
## What is an addon?
An `addon` object seems to represent a project. A modpack is an addon. A mod is also an addon.
To make this easier to understand, some attributes that are named project by the endpoint is renamed
as addon in this library.