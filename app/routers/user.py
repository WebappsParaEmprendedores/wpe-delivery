from fastapi import APIRouter

router = APIRouter(
	prefix='/auth',
	tags=['Admin']
)

@router.get('')
def test_me():
	return {'msg': 'successs', 'connected': True}