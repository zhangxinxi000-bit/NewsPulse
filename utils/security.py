"""密码加密工具：使用 bcrypt，安全地存储密码。"""
import bcrypt


def get_hash_password(password: str) -> str:
    """对明文密码加盐哈希。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # 哈希值格式不合法等情况
        return False
