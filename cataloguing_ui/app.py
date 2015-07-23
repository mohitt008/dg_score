import json
import config

from flask import Flask, render_template, request, url_for, session, redirect, Blueprint
from flask_oauthlib.client import OAuth
from pymongo import MongoClient
from utils import update_category, get_categories, get_product_tagging_details, get_vendors, get_subcategories, get_taglist, get_all_tags
from bson.objectid import ObjectId
from users import add_user, get_tag_count, inc_tag_count, get_users

bp = Blueprint('bp', __name__, static_folder='static', template_folder='templates')
app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY

client = MongoClient(connect=False)
db = client.products_db
oauth = OAuth()

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=config.FB_CONSUMER_KEY,
                            consumer_secret=config.FB_CONSUMER_SECRET,
                            request_token_params={'scope': 'email'})


@bp.route('/login/fbauthorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print('access_token')
    print(resp['access_token'])
    session['oauth_token'] = (resp['access_token'], '')

    me = facebook.get('/me')
    print(me.data)
    add_user(me.data)
    if me.data['id'] and me.data['name']:
        session['user'] = me.data
        return redirect(request.args.get('next', '/tag'))
    else:
        return "Login failed"


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@bp.route('/fb-login')
def fb_login():
    """
    The facebook login page. Clears the session before allowing a new user to authenticate.
    """
    print("login attempt")
    session.clear()
    print(request.args.get('next'))
    return facebook.authorize(callback=url_for('bp.facebook_authorized',
                                               next=request.args.get('next') or request.referrer or None,
                                               _external=True))


@bp.route('/')
def index():
    return redirect(url_for('bp.login'))

@bp.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Render the simple login page having fb icon
    '''
    return render_template('login.htm')

@bp.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(request.args.get('next') or url_for('bp.login'))


@bp.route('/vendor/tag-it')
def tag_it_vendor():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count = get_tag_count(user_id)
        return render_template("tag_product.html",
                               vendors=get_vendors(),
                               available_cats=get_categories(),
                               username=session['user']['name'],
                               user_id=user_id,
                               tag_count=tag_count,
                               tag_by='vendor',
                               autoescape=False)
    else:
        return redirect(url_for('bp.login'))

@bp.route('/get-vendor-products', methods=['GET', 'POST'])
def get_vendor_products():
    posted_data = request.get_json()
    print(posted_data)
    if posted_data['vendor'] == 'All':
        posted_data.pop("vendor", None)
    tagging_info = get_product_tagging_details(posted_data)
    if 'error' in tagging_info:
        return tagging_info
    return json.dumps(tagging_info)

@bp.route('/category/tag-it')
def tag_it_category():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count = get_tag_count(user_id)
        return render_template("tag_product.html",
                               available_cats=get_categories(),
                               available_cats1=get_categories(),
                               username=session['user']['name'],
                               user_id=user_id,
                               tag_count=tag_count,
                               tag_by='category',
                               autoescape=False)
    else:
        return redirect(url_for('bp.login'))

@bp.route('/get-category-products', methods=['GET', 'POST'])
def get_category_products():
    posted_data = request.get_json()
    print(posted_data)
    tagging_info = get_product_tagging_details(posted_data)
    if 'error' in tagging_info:
        return tagging_info
    return json.dumps(tagging_info)

@bp.route('/get-subcats', methods=['GET', 'POST'])
def get_subcats():
    posted_data = request.get_json()
    print(posted_data)
    return get_subcategories(posted_data['category_id'])

@bp.route('/change-category', methods=['GET', 'POST'])
def change_category():
    posted_data = request.get_json()
    print(posted_data)
    update_category(posted_data['id'], posted_data['category'], posted_data['subcat'])
    tag_list = get_taglist(posted_data['category'])
    tag_list.update(get_taglist(posted_data['subcat']))
    return json.dumps(tag_list)

@bp.route('/set-tags', methods=['GET', 'POST'])
def set_tags():
    posted_data = request.get_json()
    if posted_data['tags'] and (posted_data['is_dang'] or posted_data['is_xray'] or posted_data['is_dirty']):
        posted_data['done'] = True

    user_id = session['user']['id']
    posted_data['tagged_by'] = user_id
    id = posted_data.pop("id", None)

    next_name = {}
    if 'category' in posted_data:
        next_name['category'] = posted_data.pop("category")
    elif 'vendor' in posted_data and posted_data['vendor'] != 'All':
        next_name['vendor'] = posted_data.pop("vendor")
    print('####id#######next_set######posted_data####')
    print(id, next_name, posted_data)
    if posted_data['tags'] or posted_data['is_dang'] or posted_data['is_xray'] or posted_data['is_dirty']:
        db.products.update({'_id': ObjectId(id)}, {"$set": posted_data})
        inc_tag_count(user_id)

    #fetching next product tagging info
    tagging_info = get_product_tagging_details(next_name)
    tag_count = get_tag_count(user_id)
    if 'error' in tagging_info:
        return tagging_info

    tagging_info['tag_count'] = tag_count
    return json.dumps(tagging_info)

@bp.route('/leaderboard')
def view_leaderboard():
    user_id = session['user']['id']
    tag_count = get_tag_count(user_id)
    return render_template("leaderboard.html",
                           users=get_users(),
                           username=session['user']['name'],
                           user_id=user_id,
                           tag_count=tag_count)

@bp.route('/tag-list')
def get_tags():
    user_id = session['user']['id']
    tag_count = get_tag_count(user_id)
    return render_template("tag_list.html",
                           tags=get_all_tags(),
                           username=session['user']['name'],
                           user_id=user_id,
                           tag_count=tag_count)

app.register_blueprint(bp, url_prefix='/cat-ui')
if __name__ == '__main__':
    app.debug = True
    app.run()