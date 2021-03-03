import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import Layout from "./components/Layout/Layout";
import Matcher from "./containers/Matcher/Matcher";
import Results from "./containers/Results/Results"
import VerifiedMatches from "./containers/VerifiedMatches/VerifiedMatches";
import LandingPage from "./containers/LandingPage/LandingPage";
import NoMatch from "./components/UI/NoMatch/NoMatch"

class App extends Component {
  render() {
    return (
      <div>
          <Switch>
              <Route exact path="/">
                  <LandingPage/>
              </Route>
              <Route path="/verified_matches">
                  <Layout>
                      <VerifiedMatches/>
                  </Layout>
              </Route>
              <Route path="/results">
                  <Layout>
                      <Results/>
                  </Layout>
              </Route>
              <Route path="/matcher">
                  <Layout>
                      <Matcher/>
                  </Layout>
              </Route>
              <Route>
                  <NoMatch/>
              </Route>
          </Switch>
      </div>
    );
  }
}

export default App;
