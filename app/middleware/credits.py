from fastapi import Request

async def my_credits(req: Request, next):
	res = await next(req)
	res.headers['Developed-By'] = 'WPE - https://wpe.net.pe'

	return res