import React, { Component } from 'react';

import Layout from './components/Layout/Layout';
import Matcher from "./containers/Matcher/Matcher";

class App extends Component {
  render() {
    return (
      <div>
        <Layout>
          <Matcher />
        </Layout>
      </div>
    );
  }
}

export default App;
