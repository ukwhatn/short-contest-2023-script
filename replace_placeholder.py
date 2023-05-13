from xmlrpc import client as client_class
import os
import random
import dotenv
import logging

dotenv.load_dotenv()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def main():
    confirm = input(f"{os.getenv('SITE_NAME')} (y/n)")

    if confirm != "y":
        exit(1)

    with client_class.ServerProxy(
            f'https://eventbot:{os.getenv("WD_API_KEY")}@www.wikidot.com/xml-rpc-api.php') as client:
        # 対象ページ確認
        event_pages = client.pages.select({
            "site": os.getenv("SITE_NAME"),
            "categories": [
                "event"
            ],
            "tags_all": ["ショート2023"]
        })
        # fullname -> name
        event_page_names = [p.removeprefix("event:") for p in event_pages]
        # プレースホルダ確認
        placeholder_pages = client.pages.select({
            "site": os.getenv("SITE_NAME"),
            "categories": [
                "_default"
            ],
            "tags_all": ["コンテスト", "ショート2023", "jp"],
            "tags_none": ["ハブ"]
        })

        # ページごとに処理
        for p in event_page_names:
            # プレースホルダ削除
            if p in placeholder_pages:
                logger.info(f"Deleting placeholder: {p}")
                rename_to = f"deleted:placeholder-{p}-{random.randint(100, 9999)}"
                client.pages.save_one({
                    "site": os.getenv("SITE_NAME"),
                    "page": p,
                    "rename_as": rename_to,
                    "tags": [],
                    "save_mode": "update",
                    "revision_comment": "ショートコンテスト2023のプレースホルダを削除しました。"
                })
            else:
                logger.info(f"Placeholder is not found : {p}")
                if input("continue? (y/n)") != "y":
                    exit(1)

            # eventカテゴリから_defaultに移動
            logger.info(f"Renaming article page: {p}")
            client.pages.save_one({
                "site": os.getenv("SITE_NAME"),
                "page": f"event:{p}",
                "rename_as": p,
                "save_mode": "update",
                "revision_comment": "ショートコンテスト2023の投票期間開始に伴い、eventカテゴリから移動されました。"
            })


if __name__ == "__main__":
    main()
