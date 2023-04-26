from xmlrpc import client as client_class
import os
import random
import requests
import time
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

existed_pages = []


def main():
    logger.info(f"watching {os.getenv('SITE_NAME')}...")
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

        # プレースホルダが存在しないページを抽出
        new_page_names = [p for p in event_page_names if p not in placeholder_pages]
        # プレースホルダだけ存在するページを抽出
        deleted_page_names = [p for p in placeholder_pages if p not in event_page_names]

        if len(new_page_names) > 0:
            logger.info(
                f"new : {' '.join(new_page_names)}"
            )

            for p in new_page_names:
                # プレースホルダ作成
                try:
                    logger.info(f"Creating page: {p}")
                    client.pages.save_one({
                        "site": os.getenv("SITE_NAME"),
                        "page": p,
                        "title": f"ショートコンテスト2023 - {p}",
                        "parent_fullname": "shortcontest23",
                        "save_mode": "create",
                        "revision_comment": "ショートコンテスト2023のプレースホルダを作成しました。"
                    })
                    # タグ付与
                    logger.info(f"Tagging page: {p}")
                    client.pages.save_one({
                        "site": os.getenv("SITE_NAME"),
                        "page": p,
                        "tags": ["コンテスト", "ショート2023", "jp"],
                        "save_mode": "update",
                        "revision_comment": "タグ付与"
                    })
                    requests.post(
                        os.getenv("WEBHOOK_URL"),
                        {
                            "content": f"プレースホルダを作成しました: http://{os.getenv('SITE_NAME')}.wikidot.com/{p}"
                        }
                    )
                except client_class.Fault as e:
                    if "Page already exists" in e.faultString:
                        if p not in existed_pages:
                            existed_pages.append(p)
                            requests.post(
                                os.getenv("WEBHOOK_URL"),
                                {
                                    "content": f"ページが既に存在しています: http://{os.getenv('SITE_NAME')}.wikidot.com/{p}"
                                }
                            )

        if len(deleted_page_names) > 0:
            logger.info(
                f"del : {' '.join(deleted_page_names)}"
            )
            for p in deleted_page_names:
                # プレースホルダ削除
                logger.info(f"Deleting page: {p}")
                rename_to = f"deleted:placeholder-{p}-{random.randint(100, 9999)}"
                client.pages.save_one({
                    "site": os.getenv("SITE_NAME"),
                    "page": p,
                    "rename_as": rename_to,
                    "tags": [],
                    "save_mode": "update",
                    "revision_comment": "ショートコンテスト2023のプレースホルダを削除しました。"
                })
                requests.post(
                    os.getenv("WEBHOOK_URL"),
                    {
                        "content": f"プレースホルダを削除しました: http://{os.getenv('SITE_NAME')}.wikidot.com/{rename_to}"
                    }
                )


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logger.exception(e)
            pass
        time.sleep(15)
