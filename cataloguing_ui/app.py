import json
import config

from flask import Flask, render_template, request, url_for, session, redirect
from flask_oauthlib.client import OAuth
from pymongo import MongoClient
from utils import update_category, get_categories, get_product_tagging_details, get_vendors, get_subcategories
from bson.objectid import ObjectId
from users import add_user, get_tag_count, inc_tag_count, get_users

app = Flask(__name__, static_url_path='', template_folder='templates')

client = MongoClient()
db = client.products_db
oauth = OAuth()
app.secret_key = config.APP_SECRET_KEY

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=config.FB_CONSUMER_KEY,
                            consumer_secret=config.FB_CONSUMER_SECRET,
                            request_token_params={'scope': 'email'})


@app.route('/login/fbauthorized')
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


@app.route('/fb-login')
def fb_login():
    """
    The facebook login page. Clears the session before allowing a new user to authenticate.
    """
    print("login attempt")
    session.clear()
    print(request.args.get('next'))
    return facebook.authorize(callback=url_for('facebook_authorized',
                                               next=request.args.get('next') or request.referrer or None,
                                               _external=True))


@app.route('/')
def index():
    return render_template("base_tagging.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Render the simple login page having fb icon
    '''
    return render_template('login.htm')


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(request.args.get('next') or '/login')


@app.route('/vendor/tag-it')
def tag_it_vendor():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count = get_tag_count(user_id)
        return render_template("tag_vendor.html",
                               vendors=get_vendors(),
                               available_cats=get_categories(),
                               username=session['user']['name'],
                               user_id=user_id,
                               tag_count=tag_count,
                               autoescape=False)
    else:
        return redirect(url_for('login'))

@app.route('/get-vendor-products', methods=['GET', 'POST'])
def get_vendor_products():
    posted_data = request.get_json()
    print(posted_data)
    tagging_info = get_product_tagging_details(posted_data)
    if 'error' in tagging_info:
        return tagging_info
    return json.dumps(tagging_info)

@app.route('/category/tag-it')
def tag_it_category():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count = get_tag_count(user_id)
        return render_template("tag_category.html",
                               available_cats=get_categories(),
                               username=session['user']['name'],
                               user_id=user_id,
                               tag_count=tag_count,
                               autoescape=False)
    else:
        return redirect(url_for('login'))

@app.route('/get-category-products', methods=['GET', 'POST'])
def get_category_products():
    posted_data = request.get_json()
    print(posted_data)
    tagging_info = get_product_tagging_details(posted_data)
    if 'error' in tagging_info:
        return tagging_info
    return json.dumps(tagging_info)

@app.route('/get-subcats', methods=['GET', 'POST'])
def get_subcats():
    posted_data = request.get_json()
    print(posted_data)
    return get_subcategories(posted_data['category_id'])

@app.route('/confirm-category', methods=['GET', 'POST'])
def confirm_category():
    posted_data = request.get_json()
    print(posted_data)
    if posted_data['sub_category'] == 'None':
        sub_cat = None
    else:
        sub_cat = posted_data['sub_category'].split('->')[-1]

    return update_category(posted_data['id'], posted_data['category'], sub_cat)


@app.route('/change-category', methods=['GET', 'POST'])
def change_category():
    posted_data = request.get_json()
    print(posted_data)
    return update_category(posted_data['id'], posted_data['category'], posted_data['subcat'])


@app.route('/set-tags', methods=['GET', 'POST'])
def set_tags():
    posted_data = request.get_json()
    user_id = session['user']['id']
    if posted_data['tags']:
        db.products.update({'_id': ObjectId(posted_data['id'])},
                           {"$set": {'tags': posted_data['tags'],
                                     'tagged_by': user_id,
                                     'is_dang': posted_data['is_dang'],
                                     'is_xray': posted_data['is_xray'],
                                     'is_dirty': posted_data['is_dirty']}
                           })
        inc_tag_count(user_id)

    # fetching next product name
    posted_data.pop("id", None)
    posted_data.pop("tags", None)
    posted_data.pop("is_dang", None)
    posted_data.pop("is_xray", None)
    posted_data.pop("is_dirty", None)
    print(posted_data)
    tagging_info = get_product_tagging_details(posted_data)
    tag_count = get_tag_count(user_id)
    tagging_info['tag_count'] = tag_count
    if 'error' in tagging_info:
        return tagging_info
    return json.dumps(tagging_info)

@app.route('/leaderboard')
def view_leaderboard():
    return render_template("leaderboard.html", users=get_users())

if __name__ == '__main__':
    app.debug = True
    app.run()