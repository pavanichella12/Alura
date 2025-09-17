import streamlit as st
import json
from src.core.hybrid_moderator import HybridModerator
from src.core.database import ContentModerationDB
from src.utils.notifications import NotificationSystem
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)

def main():
    """Main function for cloud deployment compatibility"""
    run_app()

def run_app():
    # Set up the page
    st.set_page_config(page_title="Content Moderation System", page_icon="🛡️", layout="wide")

    # Initialize components
    @st.cache_resource
    def init_components():
        return HybridModerator(), ContentModerationDB(), NotificationSystem()

    moderator, db, notifications = init_components()

    # Initialize session state
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # User switching mechanism
    if "current_user_index" not in st.session_state:
        st.session_state.current_user_index = 0

    # Demo users for testing
    demo_users = [
        "user_1_alpha",
        "user_2_beta", 
        "user_3_gamma",
        "user_4_delta",
        "user_5_epsilon"
    ]

    # Switch user button in sidebar
    if st.sidebar.button("🔄 Switch User"):
        st.session_state.current_user_index = (st.session_state.current_user_index + 1) % len(demo_users)
        st.session_state.user_id = demo_users[st.session_state.current_user_index]
        st.session_state.messages = []  # Clear messages for new user
        st.rerun()

    # Clear data button for testing
    if st.sidebar.button("🗑️ Clear All Data (Testing)"):
        try:
            db.clear_all_data()
            st.session_state.messages = []
            st.success("✅ All data cleared! Start fresh now.")
        except AttributeError:
            # Fallback: manually clear the database
            import os
            if os.path.exists("data/content_moderation.db"):
                os.remove("data/content_moderation.db")
                st.success("✅ Database file deleted! Restart the app for fresh start.")
            else:
                st.success("✅ No existing data found!")
        st.rerun()

    # Display current user
    st.sidebar.write(f"**Current User:** {st.session_state.user_id}")
    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False
    if "modal_data" not in st.session_state:
        st.session_state.modal_data = {}

    st.title("🛡️ Content Moderation System")
    st.write("This system screens ALL messages for inappropriate language before sending.")

    # Sidebar for user info
    with st.sidebar:
        st.header("User Information")
        st.write(f"**User ID:** {st.session_state.user_id[:8]}...")
        
        # Get user violations
        violations = db.get_user_violations(st.session_state.user_id)
        st.write(f"**Violations:** {violations['violation_count']}/3")
        
        if violations['violation_count'] >= 3:
            st.error("⚠️ You have reached the violation limit!")
            st.info("Please complete the training module to continue.")
        
        # Training completion status
        if violations['training_completed']:
            st.success("✅ Training completed")
        elif violations['violation_count'] >= 3:
            st.warning("📚 Training required")
        
        # Message statistics
        stats = db.get_message_stats(st.session_state.user_id)
        st.write(f"**Total Messages:** {stats['total_messages']}")
        st.write(f"**Flagged Messages:** {stats['flagged_messages']}")
        st.write(f"**Flag Rate:** {stats['flag_rate']:.1%}")

    # Main chat interface
    st.header("💬 Message Testing")

    # User input
    if violations['violation_count'] >= 3 and not violations['training_completed']:
        st.warning("⚠️ Message input disabled - Complete training to continue")

    user_input = st.text_input("Type your message:", key=f"user_input_{st.session_state.user_id}", disabled=violations['violation_count'] >= 3)

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("Send", disabled=violations['violation_count'] >= 3):
            if user_input.strip():
                # STEP 1: Screen ALL messages before sending
                with st.spinner("Screening message..."):
                    result = moderator.analyze_message(user_input, st.session_state.user_id)
                
                # STEP 2: Store ALL messages in database (for learning and record keeping)
                if result.get("flagged", False):
                    # Store flagged message with detailed info
                    message_id = db.store_flagged_message(
                        user_id=st.session_state.user_id,
                        message=user_input,
                        flagged_words=result.get("detected_words", []),
                        categories=result.get("categories", []),
                        confidence=result.get("confidence", 0.0),
                        alternatives=result.get("alternatives", [])
                    )
                    
                    # STEP 3: Show modal/popup for flagged content
                    st.session_state.show_modal = True
                    st.session_state.modal_data = {
                        "message": user_input,
                        "result": result,
                        "message_id": message_id
                    }
                    
                    # STEP 4: Message is NOT delivered (stays in modal)
                    st.error("🚨 Message blocked - inappropriate content detected!")
                    
                else:
                    # Store clean message in database
                    db.store_clean_message(st.session_state.user_id, user_input)
                    
                    # Add to chat history if not flagged (message IS delivered)
                    st.session_state.messages.append(("You", user_input))
                    st.session_state.messages.append(("System", "✅ Message sent successfully!"))
                
                # Rerun to refresh UI
                st.rerun()

    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # Display chat history (only clean messages that were delivered)
    st.subheader("Chat History (Delivered Messages Only)")

    # Show regular chat messages
    for sender, message in st.session_state.messages:
        if sender == "You":
            st.write(f"**{sender}:** {message}")
        else:
            st.info(f"**{sender}:** {message}")

    # Show approved messages that were delivered after review
    approved_messages = db.get_approved_messages(st.session_state.user_id)
    if approved_messages:
        st.write("---")
        st.subheader("✅ Approved Messages (Delivered After Review)")
        for msg in approved_messages:
            st.success(f"**You:** {msg['message']}")
            st.caption(f"Approved on: {msg['timestamp']} - {msg['reviewer_notes']}")

    # STEP 5: Modal/popup for flagged content
    if st.session_state.show_modal:
        with st.container():
            st.markdown("---")
            st.error("🚨 **MESSAGE BLOCKED**")
            
            modal_data = st.session_state.modal_data
            result = modal_data["result"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Original Message:** {modal_data['message']}")
                st.write(f"**Detected Words:** {', '.join(result.get('detected_words', []))}")
                st.write(f"**Categories:** {', '.join(result.get('categories', []))}")
                st.write(f"**Confidence:** {result.get('confidence', 0):.2f}")
                st.write(f"**Severity:** {result.get('severity', 'medium')}")
            
            with col2:
                st.write("**Why it was flagged:**")
                st.write(result.get('context_analysis', 'No explanation provided'))
                st.write("**Reasoning:**")
                st.write(result.get('reasoning', 'No detailed reasoning provided'))
            
            # STEP 6: Suggested replacement words
            st.write("**Suggested Replacement Words:**")
            alternatives = result.get('alternatives', [])
            if alternatives:
                for alt in alternatives:
                    st.write(f"• {alt}")
            else:
                st.write("No alternatives provided")
            
            # Add a continue button to dismiss modal and start fresh
            st.write("---")
            if st.button("✅ Continue", key="continue_btn", type="primary"):
                st.session_state.show_modal = False
                st.session_state.challenge_mode = False
                st.rerun()
            
            # STEP 7: Challenge system
            st.write("---")
            st.write("**Think this was flagged incorrectly?**")
            
            # Use session state to track challenge mode
            if "challenge_mode" not in st.session_state:
                st.session_state.challenge_mode = False
            
            # Make the challenge button more prominent
            if st.button("🚨 CHALLENGE THIS DECISION", key="challenge_btn_modal", type="primary"):
                st.write("🔧 Debug: Challenge button clicked!")
                st.session_state.challenge_mode = True
                st.rerun()
            
            if st.session_state.challenge_mode:
                challenge_reason = st.text_area("Explain why you believe this was flagged incorrectly:", key="challenge_reason_text")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Submit Challenge", key="submit_challenge_btn"):
                        # Create challenge request
                        challenge_id = db.create_challenge_request(
                            flagged_message_id=modal_data["message_id"],
                            user_id=st.session_state.user_id,
                            challenge_reason=challenge_reason
                        )
                        
                        # Send WhatsApp notification to reviewer
                        challenge_data = {
                            'user_id': st.session_state.user_id,
                            'original_message': modal_data['message'],
                            'flagged_words': result.get('detected_words', []),
                            'categories': result.get('categories', []),
                            'challenge_reason': challenge_reason,
                            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Debug: Check environment variables
                        st.write(f"Debug - TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID', 'NOT SET')}")
                        st.write(f"Debug - REVIEWER_PHONE: {os.getenv('REVIEWER_PHONE', 'NOT SET')}")
                        
                        notification_sent = notifications.send_challenge_notification(challenge_data)
                        
                        if notification_sent:
                            st.success("✅ Challenge submitted successfully!")
                            st.info("📱 Notification sent (WhatsApp or fallback)")
                            st.write("🔧 Debug: Challenge saved to database and notification sent")
                        else:
                            st.error("❌ Failed to submit challenge")
                            st.write("🔧 Debug: Challenge submission failed")
                        
                        st.session_state.show_modal = False
                        st.session_state.challenge_mode = False
                        st.rerun()
                
                with col2:
                    if st.button("Cancel Challenge", key="cancel_challenge_btn"):
                        st.session_state.challenge_mode = False
                        st.rerun()
            
            # Close modal
            if st.button("Close", key="close_modal_btn"):
                st.session_state.show_modal = False
                st.rerun()

    # STEP 8: Three-strike system with training page
    if violations['violation_count'] >= 3:
        st.markdown("---")
        st.header("📚 Training Module")
        
        if not violations['training_completed']:
            st.warning("⚠️ You have used flagged words 3 times. You are now required to complete training.")
            
            # Get training content
            training_content = moderator.knowledge_injection.get_training_content()
            
            st.subheader("Understanding the Impact of Your Words")
            st.write(training_content.get("general_impact", ""))
            st.write(training_content.get("workplace_impact", ""))
            st.write(training_content.get("psychological_impact", ""))
            
            st.subheader("Why Your Language is Not Appropriate")
            guidelines = moderator.knowledge_injection.knowledge_base.get("guidelines", {})
            for guideline, description in guidelines.items():
                st.write(f"**{guideline.replace('_', ' ').title()}:** {description}")
            
            st.subheader("How to Be Better Men by Treating Women Better")
            st.write("""
            **1. Use Respectful Language:**
            - Avoid derogatory terms and stereotypes
            - Focus on women's abilities, not appearance
            - Use gender-neutral language when possible
            
            **2. Challenge Your Biases:**
            - Question why you use certain words
            - Consider the impact, not just intent
            - Learn about intersectionality
            
            **3. Be an Ally:**
            - Speak up when others use inappropriate language
            - Support women's achievements
            - Promote inclusive environments
            """)
            
            st.subheader("Alternative Language Examples")
            for category_name, category_data in moderator.knowledge_injection.knowledge_base.get("categories", {}).items():
                with st.expander(f"{category_name.replace('_', ' ').title()}"):
                    st.write(f"**Description:** {category_data['description']}")
                    st.write("**Instead of:**")
                    for word in category_data.get("words", [])[:3]:
                        st.write(f"• {word}")
                    st.write("**Try:**")
                    for alt in category_data.get("alternatives", [])[:3]:
                        st.write(f"• {alt}")
            
            # Training completion
            if st.button("Complete Training"):
                db.mark_training_completed(st.session_state.user_id)
                st.success("Training completed! You can now continue using the system.")
                st.rerun()
        else:
            st.success("✅ Training completed! You can continue using the system.")

    # Admin section (for demo purposes)
    if st.sidebar.checkbox("Show Admin Panel"):
        st.markdown("---")
        st.header("🔧 Admin Panel")
        
        # Show pending challenges
        st.subheader("Pending Challenges")
        challenges = db.get_pending_challenges()
        
        if challenges:
            for challenge in challenges:
                with st.expander(f"Challenge from {challenge['user_id'][:8]}..."):
                    st.write(f"**Original Message:** {challenge['original_message']}")
                    st.write(f"**Flagged Words:** {challenge['flagged_words']}")
                    st.write(f"**User's Reason:** {challenge['challenge_reason']}")
                    st.write(f"**Submitted:** {challenge['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Approve {challenge['challenge_id']}"):
                            # Approve the challenge - unflag and deliver the message
                            success = db.approve_challenge(challenge['challenge_id'], "Challenge approved by reviewer")
                            if success:
                                st.success("✅ Challenge approved! Message will be delivered.")
                                st.info("📱 User will be notified of approval")
                                # Send notification to user
                                notifications.send_review_notification(challenge['challenge_id'], "approved", "Challenge approved by reviewer")
                            else:
                                st.error("❌ Failed to approve challenge")
                            st.rerun()
                    with col2:
                        if st.button(f"❌ Reject {challenge['challenge_id']}"):
                            # Reject the challenge - keep message flagged and blocked
                            success = db.reject_challenge(challenge['challenge_id'], "Challenge rejected by reviewer")
                            if success:
                                st.error("❌ Challenge rejected! Message stays blocked.")
                                st.info("📱 User will be notified of rejection")
                                # Send notification to user
                                notifications.send_review_notification(challenge['challenge_id'], "rejected", "Challenge rejected by reviewer")
                            else:
                                st.error("❌ Failed to reject challenge")
                            st.rerun()
        else:
            st.info("No pending challenges")

# Run the app
if __name__ == "__main__":
    main()