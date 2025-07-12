"""
Blockchain Service
提供Web3钱包连接、智能合约交互、NFT铸造等区块链功能
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from web3 import Web3
from eth_account import Account
from eth_typing import ChecksumAddress
import ipfshttpclient
import redis
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库模型
Base = declarative_base()

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(66), unique=True, index=True)
    from_address = Column(String(42), index=True)
    to_address = Column(String(42), index=True)
    value = Column(DECIMAL(36, 18))
    gas_used = Column(Integer)
    gas_price = Column(DECIMAL(36, 18))
    status = Column(String(20))
    block_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    contract_address = Column(String(42), nullable=True)
    function_name = Column(String(100), nullable=True)
    metadata = Column(Text, nullable=True)

class ThoughtNFT(Base):
    __tablename__ = "thought_nfts"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, unique=True, index=True)
    owner_address = Column(String(42), index=True)
    thought_data = Column(Text)
    ipfs_hash = Column(String(100))
    metadata_uri = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_listed = Column(Boolean, default=False)
    price = Column(DECIMAL(36, 18), nullable=True)

class UserWallet(Base):
    __tablename__ = "user_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    wallet_address = Column(String(42), unique=True, index=True)
    encrypted_private_key = Column(Text)
    nonce = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)

# Pydantic 模型
class WalletCreate(BaseModel):
    user_id: str
    password: str

class WalletConnect(BaseModel):
    address: str
    signature: str
    message: str

class TransactionCreate(BaseModel):
    to_address: str
    value: str
    gas_limit: Optional[int] = 21000
    gas_price: Optional[str] = None
    data: Optional[str] = ""

class NFTMint(BaseModel):
    owner_address: str
    thought_data: str
    metadata: Dict[str, Any]
    price: Optional[str] = None

class SmartContractCall(BaseModel):
    contract_address: str
    function_name: str
    parameters: List[Any]
    value: Optional[str] = "0"

class BlockchainService:
    """区块链服务主类"""
    
    def __init__(self):
        self.app = FastAPI(
            title="智能思维平台 - 区块链服务",
            description="Web3钱包连接、智能合约交互、NFT铸造",
            version="1.0.0"
        )
        
        # 初始化Web3连接
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))
        self.w3_testnet = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/YOUR_PROJECT_ID"))
        
        # 初始化IPFS客户端
        try:
            self.ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        except Exception as e:
            logger.warning(f"IPFS not available: {e}")
            self.ipfs_client = None
        
        # 初始化Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # 初始化数据库
        self.engine = create_engine("sqlite:///blockchain.db")
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.get_db = lambda: SessionLocal()
        
        # 智能合约ABI（简化版）
        self.thought_nft_abi = [
            {
                "inputs": [{"name": "to", "type": "address"}, {"name": "tokenURI", "type": "string"}],
                "name": "mint",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "tokenURI",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        # 思维NFT合约地址（需要部署）
        self.thought_nft_contract_address = "0x1234567890123456789012345678901234567890"
        
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "web3_connected": self.w3.is_connected(),
                "ipfs_available": self.ipfs_client is not None,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/wallet/create")
        async def create_wallet(wallet_data: WalletCreate):
            """创建新钱包"""
            try:
                # 生成新账户
                account = Account.create()
                
                # 加密私钥
                encrypted_key = Account.encrypt(account.key, wallet_data.password)
                
                # 保存到数据库
                db = self.get_db()
                try:
                    db_wallet = UserWallet(
                        user_id=wallet_data.user_id,
                        wallet_address=account.address,
                        encrypted_private_key=json.dumps(encrypted_key)
                    )
                    db.add(db_wallet)
                    db.commit()
                    
                    return {
                        "success": True,
                        "address": account.address,
                        "message": "钱包创建成功"
                    }
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Failed to create wallet: {e}")
                raise HTTPException(status_code=500, detail="钱包创建失败")
        
        @self.app.post("/wallet/connect")
        async def connect_wallet(wallet_data: WalletConnect):
            """连接外部钱包"""
            try:
                # 验证签名
                message_hash = self.w3.keccak(text=wallet_data.message)
                recovered_address = Account.recover_message(message_hash, signature=wallet_data.signature)
                
                if recovered_address.lower() != wallet_data.address.lower():
                    raise HTTPException(status_code=400, detail="签名验证失败")
                
                # 生成访问令牌
                access_token = self.generate_access_token(wallet_data.address)
                
                # 缓存钱包状态
                self.redis_client.setex(
                    f"wallet:{wallet_data.address}",
                    3600,  # 1小时过期
                    json.dumps({
                        "address": wallet_data.address,
                        "connected_at": datetime.now().isoformat(),
                        "access_token": access_token
                    })
                )
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "address": wallet_data.address,
                    "message": "钱包连接成功"
                }
                
            except Exception as e:
                logger.error(f"Failed to connect wallet: {e}")
                raise HTTPException(status_code=500, detail="钱包连接失败")
        
        @self.app.get("/wallet/{address}/balance")
        async def get_wallet_balance(address: str):
            """获取钱包余额"""
            try:
                # 验证地址格式
                if not Web3.is_address(address):
                    raise HTTPException(status_code=400, detail="无效的钱包地址")
                
                # 获取ETH余额
                balance_wei = self.w3.eth.get_balance(address)
                balance_eth = Web3.from_wei(balance_wei, 'ether')
                
                # 获取NFT数量
                nft_count = await self.get_nft_count(address)
                
                return {
                    "address": address,
                    "eth_balance": str(balance_eth),
                    "nft_count": nft_count,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get balance: {e}")
                raise HTTPException(status_code=500, detail="获取余额失败")
        
        @self.app.post("/nft/mint")
        async def mint_thought_nft(nft_data: NFTMint, background_tasks: BackgroundTasks):
            """铸造思维NFT"""
            try:
                # 验证钱包地址
                if not Web3.is_address(nft_data.owner_address):
                    raise HTTPException(status_code=400, detail="无效的钱包地址")
                
                # 上传到IPFS
                ipfs_hash = None
                if self.ipfs_client:
                    metadata = {
                        "name": f"思维NFT #{int(time.time())}",
                        "description": "基于AI分析的思维模式NFT",
                        "thought_data": nft_data.thought_data,
                        "metadata": nft_data.metadata,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    result = self.ipfs_client.add_json(metadata)
                    ipfs_hash = result
                    metadata_uri = f"https://ipfs.io/ipfs/{ipfs_hash}"
                else:
                    # 如果IPFS不可用，使用本地存储
                    metadata_uri = f"https://api.example.com/metadata/{int(time.time())}"
                
                # 异步铸造NFT
                background_tasks.add_task(
                    self.mint_nft_async, 
                    nft_data.owner_address, 
                    metadata_uri, 
                    nft_data.thought_data,
                    ipfs_hash
                )
                
                return {
                    "success": True,
                    "message": "NFT铸造已开始",
                    "ipfs_hash": ipfs_hash,
                    "metadata_uri": metadata_uri
                }
                
            except Exception as e:
                logger.error(f"Failed to mint NFT: {e}")
                raise HTTPException(status_code=500, detail="NFT铸造失败")
        
        @self.app.get("/nft/{address}/list")
        async def list_user_nfts(address: str):
            """列出用户的NFT"""
            try:
                db = self.get_db()
                try:
                    nfts = db.query(ThoughtNFT).filter(
                        ThoughtNFT.owner_address == address
                    ).all()
                    
                    return {
                        "address": address,
                        "nfts": [
                            {
                                "token_id": nft.token_id,
                                "ipfs_hash": nft.ipfs_hash,
                                "metadata_uri": nft.metadata_uri,
                                "created_at": nft.created_at.isoformat(),
                                "is_listed": nft.is_listed,
                                "price": str(nft.price) if nft.price else None
                            }
                            for nft in nfts
                        ]
                    }
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Failed to list NFTs: {e}")
                raise HTTPException(status_code=500, detail="获取NFT列表失败")
        
        @self.app.post("/contract/call")
        async def call_smart_contract(contract_call: SmartContractCall):
            """调用智能合约"""
            try:
                # 验证合约地址
                if not Web3.is_address(contract_call.contract_address):
                    raise HTTPException(status_code=400, detail="无效的合约地址")
                
                # 这里应该根据实际合约ABI调用合约
                # 简化实现
                result = {
                    "success": True,
                    "contract_address": contract_call.contract_address,
                    "function_name": contract_call.function_name,
                    "parameters": contract_call.parameters,
                    "tx_hash": f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()}",
                    "timestamp": datetime.now().isoformat()
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to call contract: {e}")
                raise HTTPException(status_code=500, detail="合约调用失败")
        
        @self.app.get("/transactions/{address}")
        async def get_transaction_history(address: str, limit: int = 50):
            """获取交易历史"""
            try:
                db = self.get_db()
                try:
                    transactions = db.query(BlockchainTransaction).filter(
                        (BlockchainTransaction.from_address == address) | 
                        (BlockchainTransaction.to_address == address)
                    ).limit(limit).all()
                    
                    return {
                        "address": address,
                        "transactions": [
                            {
                                "tx_hash": tx.tx_hash,
                                "from_address": tx.from_address,
                                "to_address": tx.to_address,
                                "value": str(tx.value),
                                "status": tx.status,
                                "timestamp": tx.timestamp.isoformat()
                            }
                            for tx in transactions
                        ]
                    }
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Failed to get transaction history: {e}")
                raise HTTPException(status_code=500, detail="获取交易历史失败")
    
    def generate_access_token(self, address: str) -> str:
        """生成访问令牌"""
        timestamp = str(int(time.time()))
        data = f"{address}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def get_nft_count(self, address: str) -> int:
        """获取NFT数量"""
        try:
            # 如果有真实的合约，这里应该调用合约的balanceOf方法
            db = self.get_db()
            try:
                count = db.query(ThoughtNFT).filter(
                    ThoughtNFT.owner_address == address
                ).count()
                return count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to get NFT count: {e}")
            return 0
    
    async def mint_nft_async(self, owner_address: str, metadata_uri: str, thought_data: str, ipfs_hash: str):
        """异步铸造NFT"""
        try:
            # 模拟铸造过程
            await asyncio.sleep(2)  # 模拟区块链确认时间
            
            # 生成token ID
            token_id = int(time.time())
            
            # 保存到数据库
            db = self.get_db()
            try:
                db_nft = ThoughtNFT(
                    token_id=token_id,
                    owner_address=owner_address,
                    thought_data=thought_data,
                    ipfs_hash=ipfs_hash,
                    metadata_uri=metadata_uri
                )
                db.add(db_nft)
                db.commit()
                
                logger.info(f"NFT minted successfully: token_id={token_id}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to mint NFT async: {e}")

# 创建区块链服务实例
blockchain_service = BlockchainService()
app = blockchain_service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 