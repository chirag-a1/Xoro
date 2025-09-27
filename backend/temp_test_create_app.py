import traceback

try:
    from app import create_app
    app = create_app()
    print('create_app succeeded')
except Exception as e:
    print('ERROR during create_app:')
    traceback.print_exc()
