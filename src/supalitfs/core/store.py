# Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import os
from pathlib import Path
from typing import Any, List

import supabase
from lightning import CloudCompute, LightningWork


class SupabaseStorage(LightningWork, abc.ABC):
    """A custom LightningWork to Drive Supabase Bucket Operations

    # Notes
        - LightningWork [docs](https://lightning.ai/docs/app/stable/core_api/lightning_work/lightning_work.html).
        - CloudCompute [docs](https://lightning.ai/docs/app/stable/core_api/lightning_work/compute.html#cloudcompute).
        - Supabase-Py [docs](https://supabase.com/docs/reference/python/initializing).
    """

    def __init__(
        self,
        parallel=False,
        cache_calls=True,
        raise_exception=True,
        host="127.0.0.1",
        port=None,
        local_build_config=None,
        cloud_build_config=None,
        start_with_flow=True,
        cloud_compute_name="default",
        cloud_compute_disk_size=0,
        cloud_compute_idle_timeout=60,
        cloud_compute_shm_size=0,
        cloud_compute_interruptible=False,
        cloud_compute_internal_id=None,
    ):

        super().__init__(
            parallel=parallel,
            cache_calls=cache_calls,
            raise_exception=raise_exception,
            host=host,
            port=port,
            local_build_config=local_build_config,
            cloud_build_config=cloud_build_config,
            start_with_flow=start_with_flow,
            cloud_compute=CloudCompute(
                name=cloud_compute_name,
                disk_size=cloud_compute_disk_size,
                idle_timeout=cloud_compute_idle_timeout,
                shm_size=cloud_compute_shm_size,
                interruptible=cloud_compute_interruptible,
                _internal_id=cloud_compute_internal_id,
            ),
        )

    @property
    def available_buckets(self):
        """shows buckets available to user

        # Notes
            see: https://supabase.com/docs/reference/python/storage-listbuckets
        """
        return supabase.storage().list_buckets()

    def create_bucket(self, bucket_name: str):
        """creates a bucket

        # Arguments
            bucket_name: the name to use when creating the bucket

        # Notes
            see: https://supabase.com/docs/reference/python/storage-createbucket
        """
        supabase.storage().create_bucket(bucket_name)

    def retrieve_bucket(self, bucket_name: str):
        """retrieves a bucket

        # Arguments
            bucket_name: the name of the bucket to retrieve

        # Notes
            see: https://supabase.com/docs/reference/python/storage-getbucket
        """
        return supabase.storage().get_bucket(bucket_name)

    def create_signed_url(self, bucket_name: str, destination: Path | str, expiry_duration: int):
        """creates a signed url

        # Arguments
            bucket_name:
            destination:
            expiray_duration: the length of time in seconds to keep the url alive

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-createsignedurl
        """
        supabase.storage().from_(bucket_name).create_signed_url(destination, expiry_duration)

    def retrieve_public_url(self, bucket_name: str, source: Path | str):
        """Returns the URL for an asset in a public bucket

        # Arguments
            bucket_name: the name of the bucket
            source:

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-getpublicurl
        """
        supabase.storage().from_(bucket_name).get_public_url(source)

    def list_bucket_files(self, bucket_name: str) -> List[str]:
        """lists files in a user defined bucket

        # Arguments
            bucket_name: the name of the bucket to show the contents of

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-list
        """
        return supabase.storage().from_(bucket_name).list()

    def delete_files_from_bucket(self, bucket_name: str, files: List[Path | str]) -> None:
        """deletes user defined files from specified bucket

        # Arguments
            bucket_name: the name of the bucket where the files are located
            files: a Python list of files, including file format ending

        # Notes
            see: https://supabase.com/docs/reference/python/storage-deletebucket
        """
        supabase.storage().from_(bucket_name).move(*files)

    def move_files(self, bucket_name: str, files: List[Path | str]) -> None:
        """moves a list of user defined files

        # Arguments
            bucket_name: the name of the bucket where the files are located
            files: a Python list of files, including file format ending

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-move
        """
        supabase.storage().from_(bucket_name).move(*files)

    def delete_bucket(self, bucket_name: str) -> None:
        """deletes a user defined bucket

        # Arguments
            bucket_name: the name of the bucket to delete

        # Notes
            see: https://supabase.com/docs/reference/python/storage-deletebucket
        """
        supabase.storage().delete_bucket(bucket_name)

    def empty_bucket(self, bucket_name: str) -> None:
        """empties a user defined bucket

        # Arguments
            bucket_name: the name of the bucket to empty

        # Notes
            see: https://supabase.com/docs/reference/python/storage-emptybucket
        """
        supabase.storage().empty_bucket(bucket_name)

    def upload_to_bucket(self, source: Path | str, destination: Path | str, bucket_name: str) -> None:
        """uploads a file to bucket

        # Arguments
            source:
            destination:
            bucket_name:

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-upload
        """
        with open(source, "rb+"):
            supabase.storage().from_(bucket_name).upload(destination, os.path.abspath(source))

    def download_from_bucket(self, source: Path | str, bucket_name: str) -> Any:
        """downloads a file from bucket to a destination

        # Arguments
            source: the object to download
            bucket_name: the name of the bucket where source is located

        # Notes
            see: https://supabase.com/docs/reference/python/storage-from-download
        """

        with open(bucket_name, "wb+") as f:
            res = supabase.storage().from_(bucket_name).download(source)
            f.write(res)

    def mount(self) -> None:
        """mount Supabase bucket to Lightning"""

    def run(self) -> None:
        """defines run for LightningFlow"""
