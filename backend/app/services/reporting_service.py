"""
Reporting service module for analytics and statistics calculations.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqla_func, extract
from app.database import ChatHistory

logger = logging.getLogger(__name__)


async def get_total_conversations(db: AsyncSession) -> int:
		"""
		Get the total count of all conversations (messages).
		"""
		try:
				result = await db.execute(select(ChatHistory))
				all_messages = result.scalars().all()
				return len(all_messages)
		except Exception as e:
				logger.error(f"Error getting total conversations: {e}")
				raise


async def get_active_users(db: AsyncSession) -> int:
		"""
		Get the count of distinct active users (session_ids).
		"""
		try:
				result = await db.execute(select(ChatHistory.session_id).distinct())
				session_ids = result.scalars().all()
				return len(session_ids)
		except Exception as e:
				logger.error(f"Error getting active users: {e}")
				raise


async def get_avg_messages_per_chat(db: AsyncSession) -> float:
		"""
		Calculate the average number of messages per chat session.
		"""
		try:
				total = await get_total_conversations(db)
				active = await get_active_users(db)
				
				if active == 0:
						return 0.0
				
				return total / active
		except Exception as e:
				logger.error(f"Error calculating average messages per chat: {e}")
				raise


async def get_conversation_trends(db: AsyncSession) -> list:
		"""
		Get conversation trends grouped by month.
		Returns a list of dicts with month and conversation count.
		"""
		try:
				query = select(
						extract('year', ChatHistory.created_at).label('year'),
						extract('month', ChatHistory.created_at).label('month'),
						sqla_func.count(ChatHistory.id).label('count')
				).group_by(
						extract('year', ChatHistory.created_at),
						extract('month', ChatHistory.created_at)
				).order_by(
						extract('year', ChatHistory.created_at),
						extract('month', ChatHistory.created_at)
				)
				
				result = await db.execute(query)
				trend_rows = result.fetchall()
				
				months_map = {
						1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
						7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
				}
				
				conversation_trends = []
				for year, month, count in trend_rows:
						if year and month:
								conversation_trends.append({
										'month': months_map.get(int(month), 'Unknown'),
										'conversations': int(count)
								})
				
				return conversation_trends
		except Exception as e:
				logger.error(f"Error fetching conversation trends: {e}")
				raise


async def get_popular_topics(db: AsyncSession) -> list:
		"""
		Get the top 5 popular topics/keywords from user messages.
		Returns a list of dicts with topic name and engagement count.
		"""
		try:
				result = await db.execute(select(ChatHistory))
				all_messages = result.scalars().all()
				
				# Extract and count keywords from messages
				topics = {}
				common_words = {
						'what', 'how', 'when', 'where', 'why', 'can', 'the', 'a', 'an',
						'is', 'are', 'for', 'to', 'of', 'in', 'on', 'at', 'and', 'or', 'your', 'my', 'i', 'you', 
						'we', 'they', 'he', 'she', 'it', 'about', 'with', 'as', 'by', 'from', 'this', 'that', 'these', 'those',
						'need', 'be', 'have', 'has', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
				}
				
				for msg in all_messages:
						if msg.user_message:
								words = msg.user_message.lower().split()
								for word in words:
										word = word.strip('.,!?;:"')
										if len(word) > 3 and word not in common_words:
												topics[word] = topics.get(word, 0) + 1
				
				# Get top 5 topics
				top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
				
				# Map to engagement format
				popular_topics = []
				for word, count in top_topics:
						popular_topics.append({
								'topic': word,
								'engagement': count
						})
				
				return popular_topics
		except Exception as e:
				logger.error(f"Error fetching popular topics: {e}")
				raise


async def get_response_rate(db: AsyncSession) -> float:
		"""
		Calculate the response rate as percentage of messages with bot_response.
		Returns the percentage (0-100) of messages that have a bot response.
		"""
		try:
				result = await db.execute(select(ChatHistory))
				all_messages = result.scalars().all()
				
				total_messages = len(all_messages)
				if total_messages == 0:
						return 0.0
				
				# Count messages with non-empty bot_response
				messages_with_response = sum(
						1 for msg in all_messages 
						if msg.bot_response and msg.bot_response.strip()
				)
				
				response_rate = (messages_with_response / total_messages) * 100
				return round(response_rate, 1)
		except Exception as e:
				logger.error(f"Error calculating response rate: {e}")
				raise
