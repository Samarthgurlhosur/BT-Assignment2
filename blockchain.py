"""
Custom Blockchain Implementation for Land Registration
Provides immutable record of all land transactions
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, transaction: Dict[str, Any], previous_hash: str, timestamp: str = None):
        self.index = index
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now().isoformat()
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_data = {
            'index': self.index,
            'transaction': self.transaction,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> None:
        """
        Proof of Work: Find a hash that starts with specified number of zeros
        
        Args:
            difficulty: Number of leading zeros required in the hash
        """
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'transaction': self.transaction,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        }


class Blockchain:
    """Blockchain for managing land transactions"""
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions = []
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_transaction = {
            'land_id': 'GENESIS',
            'buyer_id': 'SYSTEM',
            'seller_id': 'SYSTEM',
            'amount': 0,
            'transaction_type': 'GENESIS'
        }
        genesis_block = Block(0, genesis_transaction, '0')
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Add a transaction to pending transactions
        
        Args:
            transaction: Transaction data (land_id, buyer_id, seller_id, amount)
        
        Returns:
            True if transaction is valid, False otherwise
        """
        # Validate transaction
        required_fields = ['land_id', 'buyer_id', 'seller_id', 'amount']
        if not all(field in transaction for field in required_fields):
            return False
        
        # Add metadata
        transaction['timestamp'] = datetime.now().isoformat()
        transaction['status'] = 'COMPLETED'
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_id: str) -> bool:
        """
        Mine pending transactions and add them to the blockchain
        
        Args:
            miner_id: ID of the miner (usually system or admin)
        
        Returns:
            True if mining was successful, False if no pending transactions
        """
        if not self.pending_transactions:
            return False
        
        # Combine all pending transactions into one block
        block_transaction = {
            'transactions': self.pending_transactions,
            'miner_id': miner_id,
            'transaction_count': len(self.pending_transactions)
        }
        
        previous_block = self.get_latest_block()
        new_block = Block(
            len(self.chain),
            block_transaction,
            previous_block.hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        
        return True
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain
        Checks that all hashes are correct and previous_hash pointers are valid
        
        Returns:
            True if blockchain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_blockchain(self) -> List[Dict[str, Any]]:
        """Get entire blockchain as list of dictionaries"""
        return [block.to_dict() for block in self.chain]
    
    def get_transaction_history(self, land_id: str) -> List[Dict[str, Any]]:
        """
        Get all transactions related to a specific land
        
        Args:
            land_id: ID of the land
        
        Returns:
            List of transactions for the land
        """
        transactions = []
        
        for block in self.chain:
            if 'transactions' in block.transaction:
                # Block contains multiple transactions
                for tx in block.transaction['transactions']:
                    if tx.get('land_id') == land_id:
                        transactions.append({
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'timestamp': block.timestamp,
                            **tx
                        })
            else:
                # Single transaction block (like genesis)
                if block.transaction.get('land_id') == land_id:
                    transactions.append({
                        'block_index': block.index,
                        'block_hash': block.hash,
                        'timestamp': block.timestamp,
                        **block.transaction
                    })
        
        return transactions
    
    def verify_transaction(self, land_id: str, buyer_id: str, seller_id: str) -> Dict[str, Any]:
        """
        Verify if a transaction for a land exists in the blockchain
        
        Args:
            land_id: ID of the land
            buyer_id: ID of the buyer
            seller_id: ID of the seller
        
        Returns:
            Dictionary with verification status and transaction details
        """
        transactions = self.get_transaction_history(land_id)
        
        for tx in transactions:
            if tx.get('buyer_id') == buyer_id and tx.get('seller_id') == seller_id:
                return {
                    'verified': True,
                    'transaction': tx,
                    'message': 'Transaction found in blockchain'
                }
        
        return {
            'verified': False,
            'transaction': None,
            'message': 'Transaction not found in blockchain'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        total_transactions = 0
        total_amount = 0
        
        for block in self.chain[1:]:  # Skip genesis block
            if 'transactions' in block.transaction:
                total_transactions += block.transaction['transaction_count']
                for tx in block.transaction['transactions']:
                    total_amount += tx.get('amount', 0)
            else:
                if block.transaction.get('transaction_type') != 'GENESIS':
                    total_transactions += 1
                    total_amount += block.transaction.get('amount', 0)
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_amount_transacted': total_amount,
            'chain_valid': self.is_chain_valid(),
            'pending_transactions': len(self.pending_transactions)
        }
