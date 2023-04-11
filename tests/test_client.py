from pytest import fixture, mark

from flaticon import FlatIconClient

pytestmark = mark.asyncio


@fixture
def client() -> FlatIconClient:
    return FlatIconClient()


async def test_download(client: FlatIconClient):
    images = await client.search_for_images("cat", count=2)
    image_paths = [await client.download_image(image) for image in images]
    assert image_paths
