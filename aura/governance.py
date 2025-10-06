"""
AURA Governance System
Democratic control over system parameters and strategies
"""
import logging
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .database import db

logger = logging.getLogger(__name__)


class GovernanceSystem:
    """
    Governance system for AURA:
    - Proposals for parameter changes
    - Voting mechanisms
    - Multi-signature approvals
    - Emergency pause system
    """

    def __init__(self):
        self.db = db
        self._init_governance_tables()

    def _init_governance_tables(self):
        """Initialize governance database tables"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()

                # Proposals table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS governance_proposals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        proposal_type TEXT NOT NULL,  -- 'parameter_change', 'strategy_update', 'emergency_action'
                        proposed_changes TEXT NOT NULL,  -- JSON
                        created_by INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        voting_ends_at DATETIME NOT NULL,
                        status TEXT DEFAULT 'active',  -- 'active', 'passed', 'rejected', 'executed'
                        execution_date DATETIME,
                        FOREIGN KEY (created_by) REFERENCES user_profiles(id)
                    )
                """)

                # Votes table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS governance_votes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proposal_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        vote TEXT NOT NULL,  -- 'for', 'against', 'abstain'
                        voting_power REAL DEFAULT 1.0,
                        voted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (proposal_id) REFERENCES governance_proposals(id),
                        FOREIGN KEY (user_id) REFERENCES user_profiles(id),
                        UNIQUE(proposal_id, user_id)
                    )
                """)

                # Multi-sig approvers table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS multisig_approvers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        approval_weight REAL DEFAULT 1.0,
                        is_active INTEGER DEFAULT 1,
                        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_profiles(id)
                    )
                """)

                # Approvals table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS proposal_approvals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proposal_id INTEGER NOT NULL,
                        approver_id INTEGER NOT NULL,
                        approved INTEGER DEFAULT 0,
                        approved_at DATETIME,
                        comment TEXT,
                        FOREIGN KEY (proposal_id) REFERENCES governance_proposals(id),
                        FOREIGN KEY (approver_id) REFERENCES multisig_approvers(id),
                        UNIQUE(proposal_id, approver_id)
                    )
                """)

                conn.commit()
                logger.info("Governance tables initialized")

        except Exception as e:
            logger.error(f"Governance table init error: {e}")

    def create_proposal(
        self,
        title: str,
        description: str,
        proposal_type: str,
        proposed_changes: Dict,
        created_by: int = 1,
        voting_duration_days: int = 3,
    ) -> int:
        """
        Create a new governance proposal
        Returns proposal ID
        """
        try:
            import json

            voting_ends = datetime.now() + timedelta(days=voting_duration_days)

            with self.db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO governance_proposals
                    (title, description, proposal_type, proposed_changes, created_by, voting_ends_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    title,
                    description,
                    proposal_type,
                    json.dumps(proposed_changes),
                    created_by,
                    voting_ends.isoformat(),
                ))
                conn.commit()

                proposal_id = cur.lastrowid
                logger.info(f"Proposal {proposal_id} created: {title}")
                return proposal_id

        except Exception as e:
            logger.error(f"Create proposal error: {e}")
            return -1

    def cast_vote(
        self,
        proposal_id: int,
        user_id: int,
        vote: str,
        voting_power: float = 1.0,
    ) -> bool:
        """
        Cast a vote on a proposal
        vote: 'for', 'against', 'abstain'
        """
        try:
            if vote not in ['for', 'against', 'abstain']:
                logger.warning(f"Invalid vote type: {vote}")
                return False

            # Check if proposal is still active
            proposal = self.get_proposal(proposal_id)
            if not proposal or proposal['status'] != 'active':
                logger.warning(f"Proposal {proposal_id} not active")
                return False

            # Check if voting period has ended
            if datetime.fromisoformat(proposal['voting_ends_at']) < datetime.now():
                logger.warning(f"Voting period ended for proposal {proposal_id}")
                return False

            with self.db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO governance_votes (proposal_id, user_id, vote, voting_power)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(proposal_id, user_id) DO UPDATE SET
                        vote = excluded.vote,
                        voting_power = excluded.voting_power,
                        voted_at = CURRENT_TIMESTAMP
                """, (proposal_id, user_id, vote, voting_power))
                conn.commit()

            logger.info(f"Vote cast: Proposal {proposal_id}, User {user_id}, Vote: {vote}")
            return True

        except Exception as e:
            logger.error(f"Cast vote error: {e}")
            return False

    def get_proposal(self, proposal_id: int) -> Optional[Dict]:
        """Get proposal details"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                cur.execute("""
                    SELECT id, title, description, proposal_type, proposed_changes,
                           created_by, created_at, voting_ends_at, status, execution_date
                    FROM governance_proposals
                    WHERE id = ?
                """, (proposal_id,))

                row = cur.fetchone()
                if not row:
                    return None

                return {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'proposal_type': row[3],
                    'proposed_changes': json.loads(row[4]),
                    'created_by': row[5],
                    'created_at': row[6],
                    'voting_ends_at': row[7],
                    'status': row[8],
                    'execution_date': row[9],
                }

        except Exception as e:
            logger.error(f"Get proposal error: {e}")
            return None

    def get_voting_results(self, proposal_id: int) -> Dict:
        """
        Get current voting results for a proposal
        """
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()

                cur.execute("""
                    SELECT vote, SUM(voting_power) as total_power, COUNT(*) as vote_count
                    FROM governance_votes
                    WHERE proposal_id = ?
                    GROUP BY vote
                """, (proposal_id,))

                results = {
                    'for': {'power': 0, 'count': 0},
                    'against': {'power': 0, 'count': 0},
                    'abstain': {'power': 0, 'count': 0},
                }

                for row in cur.fetchall():
                    vote_type = row[0]
                    total_power = float(row[1])
                    count = int(row[2])

                    results[vote_type] = {
                        'power': total_power,
                        'count': count,
                    }

                total_power = sum(r['power'] for r in results.values())

                return {
                    'results': results,
                    'total_voting_power': total_power,
                    'turnout': total_power,
                }

        except Exception as e:
            logger.error(f"Get voting results error: {e}")
            return {'results': {}, 'total_voting_power': 0}

    def finalize_proposal(self, proposal_id: int) -> bool:
        """
        Finalize a proposal after voting period ends
        Updates status to 'passed' or 'rejected'
        """
        try:
            proposal = self.get_proposal(proposal_id)
            if not proposal:
                return False

            # Check if voting period has ended
            if datetime.fromisoformat(proposal['voting_ends_at']) > datetime.now():
                logger.warning(f"Voting period not ended for proposal {proposal_id}")
                return False

            # Get voting results
            results = self.get_voting_results(proposal_id)
            for_power = results['results']['for']['power']
            against_power = results['results']['against']['power']

            # Determine if passed (simple majority)
            passed = for_power > against_power

            new_status = 'passed' if passed else 'rejected'

            with self.db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE governance_proposals
                    SET status = ?
                    WHERE id = ?
                """, (new_status, proposal_id))
                conn.commit()

            logger.info(f"Proposal {proposal_id} finalized: {new_status}")
            return True

        except Exception as e:
            logger.error(f"Finalize proposal error: {e}")
            return False

    def execute_proposal(self, proposal_id: int) -> bool:
        """
        Execute a passed proposal
        Apply the proposed changes to system config
        """
        try:
            proposal = self.get_proposal(proposal_id)
            if not proposal or proposal['status'] != 'passed':
                logger.warning(f"Proposal {proposal_id} not ready for execution")
                return False

            changes = proposal['proposed_changes']

            # Apply changes based on proposal type
            if proposal['proposal_type'] == 'parameter_change':
                for key, value in changes.items():
                    self.db.set_config(key, value)
                    logger.info(f"Applied config change: {key} = {value}")

            elif proposal['proposal_type'] == 'strategy_update':
                # Handle strategy updates
                pass

            elif proposal['proposal_type'] == 'emergency_action':
                # Handle emergency actions
                pass

            # Mark as executed
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE governance_proposals
                    SET status = 'executed', execution_date = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), proposal_id))
                conn.commit()

            logger.info(f"Proposal {proposal_id} executed successfully")
            return True

        except Exception as e:
            logger.error(f"Execute proposal error: {e}")
            return False

    def get_active_proposals(self) -> List[Dict]:
        """Get all active proposals"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                cur.execute("""
                    SELECT id, title, description, proposal_type, proposed_changes,
                           created_by, created_at, voting_ends_at, status
                    FROM governance_proposals
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                """)

                proposals = []
                for row in cur.fetchall():
                    proposals.append({
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'proposal_type': row[3],
                        'proposed_changes': json.loads(row[4]),
                        'created_by': row[5],
                        'created_at': row[6],
                        'voting_ends_at': row[7],
                        'status': row[8],
                    })

                return proposals

        except Exception as e:
            logger.error(f"Get active proposals error: {e}")
            return []


# Singleton instance
governance = GovernanceSystem()
