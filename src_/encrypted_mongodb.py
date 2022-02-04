'''
# ref: https://www.mongodb.com/developer/quickstart/python-quickstart-fle/
# python -m pip install "pymongo[encryption,srv]~=3.11"

client = pymongo.MongoClient(
"mongodb+srv://<id>:<password>@blogdistribution.lyfew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.test

'''
import json
import os
from datetime import datetime
from pathlib import Path
from pprint import pprint

from bson import json_util
from bson.codec_options import CodecOptions
from bson.binary import STANDARD
from pymongo import MongoClient, WriteConcern
from pymongo.encryption import ClientEncryption, Algorithm
from pymongo.encryption_options import AutoEncryptionOpts

from src_ import vars_


def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # The MongoDB namespace (db.collection) used to store the
    # password = getpass.getpass('mongoDB pw: ') # pycharm 자체콘솔에서는 작동 안 하나 봄
    password = input('mongoDB db_name: ')
    with open(os.path.join(vars_.dir_path, vars_.ids), 'r', encoding='utf-8') as f:
        id_ = json.load(f)['mongoDB']
    MDB_URL = f"mongodb+srv://{id_}:{password}@blogdistribution.lyfew.mongodb.net"
    # This must be the same master key that was used to create
    # the encryption key.
    local_master_key = os.urandom(96)
    Path(vars_.bkeys).write_bytes(local_master_key)
    kms_providers = {"local": {"key": local_master_key}}

    # The MongoDB namespace (db.collection) used to store
    # the encryption data keys.
    key_vault_namespace = "bd_config.__keystore"
    key_vault_db_name, key_vault_coll_name = key_vault_namespace.split(".", 1)

    csfle_opts = AutoEncryptionOpts(
        kms_providers=kms_providers,
        key_vault_namespace=key_vault_namespace
    )
    # The MongoClient used to access the key vault (key_vault_namespace).
    with MongoClient(MDB_URL, auto_encryption_opts=csfle_opts) as client:

        print("Resetting demo database & keystore ...")
        client.drop_database(key_vault_db_name)

        # key_vault = __keystore 테이블임
        key_vault = client[key_vault_db_name][key_vault_coll_name]
        # Ensure that two data keys cannot share the same keyAltName.
        # key_vault.drop()
        #
        # # 테이블에 인덱스 생성
        # key_vault.create_index(
        #     "keyAltNames",
        #     unique=True,
        #     partialFilterExpression={"keyAltNames": {"$exists": True}})

        # 여기가 마스터키로 데이터키 만드는 부분
        client_encryption = ClientEncryption(
            kms_providers,
            key_vault_namespace,
            client,
            # The CodecOptions class used for encrypting and decrypting.
            # This should be the same CodecOptions instance you have configured
            # on MongoClient, Database, or Collection. We will not be calling
            # encrypt() or decrypt() in this example so we can use any
            # CodecOptions.
            CodecOptions(uuid_representation=STANDARD))

        # Create a new data key and json schema for the encryptedField.
        print("Creating key in MongoDB ...")
        data_key_id = client_encryption.create_data_key(kms_provider='local', key_alt_names=['keys'])
        # db 컬렉션에서 altname으로 데이터키 가져오기
        # key_id = db.__keystore.find_one({ "keyAltNames": "example" })["_id"]
        print('scheme.......')
        schema = {
            "bsonType": "object",
            "properties": {
                "keys": {
                    "encrypt": {
                        "keyId": [data_key_id],
                        "bsonType": "object",
                        "algorithm": Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random
                    }
                }
            }
        }

        json_schema = json_util.dumps(schema,
                                      json_options=json_util.CANONICAL_JSON_OPTIONS,
                                      indent=2)
        Path("../config/json_schema.json").write_text(json_schema)

    # 키랑 스키마 다시 받아오는 건데 참조용으로 달아둠
    # Load the master key from 'key_bytes.bin':
    # key_bin = Path("key_bytes.bin").read_bytes()

    # Load the 'person' schema from "json_schema.json":
    collection_schema = json_util.loads(Path("../config/json_schema.json").read_text())

    # auto_encryption_opts=csfle_opts 이게 없으면 find_one할 때 암호화된 상태로 보여줌
    with MongoClient(MDB_URL, auto_encryption_opts=csfle_opts) as client:
        db_namespace = 'bd_config.keys'
        db_name, coll_name = db_namespace.split(".", 1)

        # key_vault_db_name, key_vault_coll_name
        db = client[db_name]
        # Clear old data
        db.drop_collection(coll_name)

        # Create the collection with the encryption JSON Schema.
        db.create_collection(
            coll_name,
            # uuid_representation=STANDARD is required to ensure that any
            # UUIDs in the $jsonSchema document are encoded to BSON Binary
            # with the standard UUID subtype 4. This is only needed when
            # running the "create" collection command with an encryption
            # JSON Schema.
            codec_options=CodecOptions(uuid_representation=STANDARD),
            write_concern=WriteConcern(w="majority"),
            validator={"$jsonSchema": collection_schema})
        coll = client[db_name][coll_name]

        with open(os.path.join(dir_path, '../config', 'config.json'), 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        config_data['updated_at'] = datetime.utcnow()
        k_id_ = coll.insert_one(config_data).inserted_id
        print('k_id_:', k_id_)
        pprint(coll.find_one())


def update_config(password):
    ''' key update 함수

    :param password:
    :return:
    '''
    from pymongo import MongoClient
    from pymongo.encryption import (Algorithm,
                                    ClientEncryption)
    from pymongo.encryption_options import AutoEncryptionOpts
    from pymongo.write_concern import WriteConcern
    from pathlib import Path

    dir_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(vars_.dir_path, '../config', 'ids.json'), 'r', encoding='utf-8') as f:
        id_ = json.load(f)['mongoDB']
    MDB_URL = f"mongodb+srv://{id_}:{password}@blogdistribution.lyfew.mongodb.net"
    key_vault_namespace = "bd_config.__keystore"

    # Load the master key from 'key_bytes.bin':
    key_bin = Path(os.path.join(dir_path, "../config/key_bytes.bin")).read_bytes()
    kms_providers = {"local": {"key": key_bin}}

    csfle_opts = AutoEncryptionOpts(
        kms_providers=kms_providers,
        key_vault_namespace=key_vault_namespace
    )

    with open(os.path.join(dir_path, '../config', 'config.json'), 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # config_ = None
    # auto_encryption_opts=csfle_opts 이게 없으면 find_one할 때 암호화된 상태로 보여줌
    # with MongoClient(MDB_URL, auto_encryption_opts=csfle_opts, ssl=True, ssl_cert_reqs='CERT_NONE') as client:
    with MongoClient(MDB_URL,
                     auto_encryption_opts=csfle_opts,
                     ssl=True,
                     tlsAllowInvalidCertificates=True) as client:

        db_namespace = 'bd_config.keys'
        db_name, coll_name = db_namespace.split(".", 1)

        coll = client[db_name][coll_name]
        config_ = coll.find_one()
        print('old config (will be deleted):')
        pprint(config_)
        coll.update_one({'_id': config_['_id']},
                        {'$set': {
                            'keys': config_data['keys'],
                            'repo': config_data['repo']
                        }})

        print('New config:')
        pprint(coll.find_one())
    # CRUD 참조: https://www.mongodb.com/developer/quickstart/python-quickstart-crud/


if __name__ == "__main__":

    password = input('mongoDB pw: ')
    update_config(password)

