"""
测试OSS配置是否正确
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.oss_uploader import oss_uploader


def test_oss_config():
    """测试OSS配置"""
    print("=" * 60)
    print("测试阿里云OSS配置")
    print("=" * 60)

    if not oss_uploader.use_oss:
        print("❌ OSS未正确配置")
        print("\n请检查.env文件中的以下配置:")
        print("  - OSS_ACCESS_KEY_ID")
        print("  - OSS_ACCESS_KEY_SECRET")
        print("  - OSS_BUCKET_NAME")
        print("  - OSS_ENDPOINT")
        print("  - OSS_URL")
        return False

    print("✅ OSS配置正确")
    print(f"\nBucket: {oss_uploader.bucket_name}")
    print(f"Endpoint: {oss_uploader.endpoint}")
    print(f"Base URL: {oss_uploader.base_url}")

    # 测试上传一个小文件
    print("\n测试上传功能...")

    # 创建一个测试文件
    test_file = "test_oss_upload.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("这是OSS测试文件")

    try:
        object_name = f"test/{test_file}"
        url = oss_uploader.upload_file(test_file, object_name)
        print(f"✅ 上传成功!")
        print(f"文件URL: {url}")

        # 测试删除
        print("\n测试删除功能...")
        success = oss_uploader.delete_file(object_name)
        if success:
            print("✅ 删除成功")
        else:
            print("⚠️ 删除失败")

        # 清理测试文件
        os.remove(test_file)

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

        return False


if __name__ == "__main__":
    success = test_oss_config()

    print("\n" + "=" * 60)
    if success:
        print("✅ OSS配置测试通过！可以正常使用")
    else:
        print("❌ OSS配置测试失败，请检查配置")
    print("=" * 60)