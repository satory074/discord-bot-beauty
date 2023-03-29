import json
import os
from typing import Optional, Union
from urllib import request

import requests
from dropbox import Dropbox
from dropbox.exceptions import ApiError
from dropbox.files import ListFolderResult, WriteMode
from dropbox.sharing import (
    ListSharedLinksResult,
    RequestedVisibility,
    SharedLinkMetadata,
    SharedLinkSettings,
)

from botutility import BotUtility


class MyDropbox:
    def __init__(self) -> None:
        self.botutil: BotUtility = BotUtility()
        TOKEN_DROPBOX: str = self.botutil.get_environvar("TOKEN_DROPBOX")
        self.dbx: Dropbox = Dropbox(TOKEN_DROPBOX)

    def get_sharedlink(self, path: str) -> Optional[str]:
        """Dropboxの共有リンクを取得する"""

        # Get dropbox shared link
        link_list: Optional[
            ListSharedLinksResult.links
        ] = self.dbx.sharing_list_shared_links(path=path, direct_only=True)

        if link_list.links:  # Existing dropbox shared link
            link: str = link_list.links[0].url
        else:  # Create dropbox shared link
            setting: SharedLinkSettings = SharedLinkSettings(
                requested_visibility=RequestedVisibility.public
            )

            # Get
            ret: Optional[
                Union[SharedLinkMetadata, ApiError]
            ] = self.dbx.sharing_create_shared_link_with_settings(
                path=path, settings=setting
            )

            # Error
            if ret is ApiError:
                print(ApiError)
                return None

            if ret:
                link: str = ret.url
            else:  # Error
                print("UBB > ERROR: Dropboxの共有リンクを取得できませんでした")
                return None

        # Format dropbox shared link
        link = link.replace("www.dropbox", "dl.dropboxusercontent")
        link = link.replace("?dl=0", "")

        return link

    def get_filelist(self, path: str) -> Optional[list[str]]:
        """Dropboxのファイルリスト名を取得する"""

        ret: ListFolderResult.cursor
        if ret := self.dbx.files_list_folder(path=path):
            return [f.name for f in ret.entries]
        else:
            print("ERROR: Dropboxのファイルリストを取得できませんでした")
            print(self.dbx.files_list_folder(path=path))

            return None

    def get_profile(self) -> Optional[dict[str, dict[str, str]]]:
        """プロフィールデータを取得する"""

        path: str = "/discord/data/profile.json"
        link: Optional[str] = self.get_sharedlink(path=path)

        if link:
            with request.urlopen(link) as f:
                d: dict[str, dict[str, str]] = json.load(f)

            return d
        else:  # Error
            return None

    def read_json(self, path: str) -> dict[str, str]:
        """DropboxのJSONファイルを読み込む"""

        link: Optional[str] = self.get_sharedlink(path=path)
        if link:
            with request.urlopen(link) as f:
                df: dict[str, str] = json.load(f)

            return df
        else:  # Error
            return {}

    def upload_json(self, df: dict[str, str], path: str, name: str) -> str:
        """DropboxにJSONファイルをアップロードする"""
        with open("tmp.json", mode="w") as f:
            json.dump(df, f, ensure_ascii=False)

        tmppath: str = "tmp.json"
        with open(tmppath, "rb") as f:
            self.dbx.files_upload(
                f.read(), mode=WriteMode.overwrite, path=f"{path}{name}",
            )

        # Remove temporally file
        os.remove("tmp.json")

        return "SUCCESS"

    def upload_image(self, url: str, path: str, ext: str = ".png") -> str:
        img_file: bytes = requests.get(f"{url}{ext}").content

        # Save avatar image temporally
        with open("tmp.png", mode="wb") as f:
            f.write(img_file)

        # Upload image to dropbox
        try:
            with open("tmp.png", "rb") as f:
                self.dbx.files_upload(f.read(), path=f"{path}{ext}")

            reply: str = f"upload: {path}{ext}"
        except ApiError:  # Deplicate name
            print("ERROR: Dropboxにアップロードできませんでした")
            print(ApiError)

            reply: str = "UBB > ERROR: その名前はむり！"

        # Remove temporally file
        os.remove("tmp.png")

        return reply
