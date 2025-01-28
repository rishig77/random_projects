#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

#define F first
#define S second
#define all(x) x.begin(), x.end()
#define int ll

vector<ll> segTree;
ll n;

void buildSegTree(ll size) {
    segTree.assign(4 * size, 0);
}

void update(ll node, ll start, ll end, ll idx, ll value) {
    if (start == end) {
        segTree[node] += value; // Point update
    } else {
        ll mid = (start + end) / 2;
        if (idx <= mid)
            update(2 * node, start, mid, idx, value);
        else
            update(2 * node + 1, mid + 1, end, idx, value);
        
        segTree[node] = segTree[2 * node] + segTree[2 * node + 1];
    }
}

ll query(ll node, ll start, ll end, ll l, ll r) {
    if (r < start || l > end) return 0; // Out of range
    if (l <= start && end <= r) return segTree[node]; // Complete overlap

    ll mid = (start + end) / 2;
    ll leftSum = query(2 * node, start, mid, l, r);
    ll rightSum = query(2 * node + 1, mid + 1, end, l, r);
    return leftSum + rightSum;
}


ll rnd(ll l, ll r) {
    mt19937_64 gen(chrono::steady_clock::now().time_since_epoch().count());
    uniform_int_distribution<ll> dist(l, r);
    return dist(gen);
}

bool cmp(pair<pair<int,int>,int>&x, pair<pair<int,int>,int>&y)
{
    auto [l1,r1] = x.first;
    auto [l2,r2] = y.first;

    if(r1==r2) return l1<l2;
    return r1<r2;
}

void solve() {
    ll k;
    cin >> n >> k;

    set<ll> s;
    vector<ll> a(n);
    vector<pair<pair<int,int>,int>>rules(k);
    map<ll, ll> mp;

    for (auto& x : a) {
        cin >> x;
        s.insert(x);
    }


    for (pair<pair<int,int>,int> &x : rules) {
        cin >> x.F.F >> x.F.S >> x.S;
        s.insert(x.F.F);
        s.insert(x.F.S);
    }


    vector<ll> pm(all(s));
    pm.insert(pm.begin(), 0);
    for (int i = 1; i < (int) pm.size(); i++)
        mp[pm[i]] = i;

    ll m = pm.size() - 1;

    buildSegTree(m);

    multiset<ll> ms;
    for (int& x : a) {
        x = mp[x];
        ms.insert(x);
    }

    for(int i=0; i<(int)rules.size(); ++i)
    {
        rules[i].first.first = mp[rules[i].first.first];
        rules[i].first.second = mp[rules[i].first.second];
    }

    ll ans = 0;


    sort(rules.begin(),rules.end(),cmp);

    for (auto [x,w] : rules) {
        auto [l,r] = x;
        if (query(1, 1, m, l, r) < w) {
            ll need = w - query(1, 1, m, l, r);
            ans = ans+need;
            for(int i=0; i<need; ++i)
            {
                auto it = ms.upper_bound(r);
                it--;
                update(1, 1, m, *it, 1);
                ms.erase(it);
            }
        }
    }

    cout << n - ans << '\n';
}

signed main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL), cout.tie(NULL);
    int t;
    cin >> t;
    while(t--) solve();
}
