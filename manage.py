from flask_script import Manager, Server
from app import app, db, member, inorout, product, purchase


# 設置你的 app
manager = Manager(app)
# 設置 python manage.py runserver 為啟動 server 指令
server = Server(host="0.0.0.0")
manager.add_command('runserver', Server()) 
# 設置 python manage.py shell 為啟動交互式指令 shell 的指令
@manager.shell
def make_shell_context():
    return dict(
        app=app, db=db, member=member, inorout=inorout, product=product, purchase=purchase)

if __name__ == '__main__':
    manager.run()
