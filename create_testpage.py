import logging
import os
from xmlrpc import client as client_class
import random, string
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def randomname(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])


def main():
    with client_class.ServerProxy(
            f'https://eventbot:{os.getenv("WD_API_KEY")}@www.wikidot.com/xml-rpc-api.php') as client:
        # name生成
        names = [randomname(10) for _ in range(10)]

        # プレースホルダ作成
        for p in names:
            logger.info(f"Creating placeholder: {p}")
            client.pages.save_one({
                "site": "pseudo-scp-jp",
                "page": p,
                "save_mode": "create",
                "revision_comment": "テスト用ページを作成しました。"
            })
            client.pages.save_one({
                "site": "pseudo-scp-jp",
                "page": p,
                "tags": ["コンテスト", "ショート2023", "jp"],
                "save_mode": "update",
                "revision_comment": "タグ付与"
            })

            logger.info(f"Creating page: event:{p}")
            client.pages.save_one({
                "site": "pseudo-scp-jp",
                "page": f"event:{p}",
                "save_mode": "create",
                "revision_comment": "テスト用ページを作成しました。"
            })
            client.pages.save_one({
                "site": "pseudo-scp-jp",
                "page": f"event:{p}",
                "tags": ["ショート2023", "jp"],
                "save_mode": "update",
                "revision_comment": "タグ付与"
            })


if __name__ == "__main__":
    main()
