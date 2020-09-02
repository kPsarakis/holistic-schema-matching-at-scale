import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';

import Layout from './components/Layout/Layout';
import Matcher from './containers/Matcher/Matcher';
import Results from './containers/Results/Results'

class App extends Component {
  render() {
    return (
      <div>
        <Layout>
            <Switch>
                <Route path={"/results"} component={Results} />
                <Route path={"/" } exact component={Matcher} />
            </Switch>
        </Layout>
      </div>
    );
  }
}

export default App;
