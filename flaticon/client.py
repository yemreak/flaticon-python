from __future__ import annotations

from os import makedirs
from pathlib import Path
from typing import Any

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from .utils import download

from .models import Image, OrderBy, Shape


class FlatIconClient:
    datapath: Path

    _session: ClientSession
    _csv_file: Path

    def __init__(self, relative_path: str = "flaticon") -> None:
        self.datapath = Path.home() / relative_path
        self._csv_file = self.datapath / "images.csv"

        makedirs(self.datapath, exist_ok=True)
        if not self._csv_file.exists():
            self._csv_file.touch()
            self._csv_file.write_text(",".join(Image.__annotations__))

    async def __aenter__(self):
        self._session = ClientSession()
        return self

    async def __aexit__(self, *args: Any):
        await self._session.close()

    async def search_for_images(
        self,
        query: str,
        shape: Shape = Shape.ALL_SHAPES,
        order_by: OrderBy = OrderBy.POPULER,
        count: int = 10,
    ) -> list[Image]:
        """Search query for flat icon

        Args:
            query (str): Image name
            shape (Shape, optional): Flat icon shapes. Defaults to "".
            order_by (OrderBy, optional): Order type. Defaults to 4.

        Returns:
            list[str]: Url of images
        """

        def create_url():
            url = f"https://www.flaticon.com/search?word={query}"
            if shape != Shape.ALL_SHAPES:
                url += f"&shape={shape.value}"
            url += f"&order_by={order_by}"
            return url

        images: list[Image] = []
        async with self._session.get(create_url()) as page:
            soup = BeautifulSoup(str(await page.content.read()), "html.parser")
            results = soup.find_all("li", class_="icon--item")
            for result in results[:count]:
                try:
                    image_url = Image(
                        id=result["data-png"]
                        .split("?")[0]
                        .split("/")[-1]
                        .split(".")[0],
                        name=result["data-name"],
                        url=result["data-png"],
                        downloads=result.get("data-downloads", 0),
                        pack=result.get("data-pack_name", "Unknown"),
                    )
                    images.append(image_url)
                except:  # Perevents any error related by ads
                    pass
        return images

    async def download_image(self, image: Image) -> Path:
        imagepath = self.datapath / f"{image.id}.png"
        with self._csv_file.open("r") as csv_file:
            for line in csv_file.readlines():
                if str(image.id) in line.split(",")[0]:
                    return imagepath
        await download(image.url, imagepath, self._session)
        with self._csv_file.open("a") as file:
            file.write("\n" + ",".join(image.to_dict().values()))
        return imagepath
