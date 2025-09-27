# backend/utils/notification.py

def send_trade_confirmation_notification(user_id: int, symbol: str, quantity: int, price: float, order_type: str):
    """
    Sends a confirmation notification for a completed trade.

    This is currently a mock implementation. In a production environment, this function
    would integrate with a push notification service like Firebase Cloud Messaging (FCM)
    or Apple Push Notification Service (APNS).

    To implement this for real, you would need to:
    1.  Store user device tokens in the User model.
    2.  Use a library (e.g., pyfcm) to send a payload to the FCM/APNS servers.
    3.  The user's mobile app would then receive and display the push notification.

    Args:
        user_id: The ID of the user who made the trade.
        symbol: The stock symbol that was traded.
        quantity: The number of shares traded.
        price: The price per share.
        order_type: The type of order ("BUY" or "SELL").
    """
    # Simulate sending a notification by printing to the console.
    # The `title` and `body` are what would typically appear on the user's device.
    title = "Trade Executed!"
    body = (
        f"Your {order_type.upper()} order for {quantity} share(s) of "
        f"{symbol.upper()} at ₹{price:.2f} has been successfully executed."
    )
    
    print("--- Sending Push Notification ---")
    print(f"User ID: {user_id}")
    print(f"Title: {title}")
    print(f"Body: {body}")
    print("---------------------------------")
    
    # In a real implementation, you would return a success/failure status.
    return True
