import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import Layout from "./components/Layout/Layout";
import Matcher from "./containers/Matcher/Matcher";
import AlgorithmEvaluation from "./containers/AlgorithmEvaluation/AlgorithmEvaluation"
import DatasetFabrication from "./containers/DatasetFabrication/DatasetFabrication"
import EvaluationResults from "./containers/EvaluationResults/EvaluationResults"
import GetFabricated from "./containers/GetFabricated/GetFabricated"
import Results from "./containers/Results/Results"
import VerifiedMatches from "./containers/VerifiedMatches/VerifiedMatches";
import LandingPage from "./containers/LandingPage/LandingPage";
import NoMatch from "./components/UI/NoMatch/NoMatch"

class App extends Component {

    render() {

        const researchToolbarElements = [
            {
                link: "/matcher",
                text: "Matcher"
            },
            {
                link: "/results",
                text: "Results"
            },
            {
                link: "/verified_matches",
                text: "Verified Matches"
            }
        ]

        const dataLakeToolbarElements = [
            {
                link: "/dataset_fabrication",
                text: "Dataset Fabrication"
            },
            {
                link: "/get_fabricated",
                text: "Get Fabricated"
            },
            {
                link: "/algorithm_evaluation",
                text: "Algorithm Evaluation"
            },
            {
                link: "/evaluation_results",
                text: "Evaluation Results"
            }
        ]

        return (
          <div>
              <Switch>
                  <Route exact path="/">
                      <LandingPage/>
                  </Route>
                  <Route path="/verified_matches">
                      <Layout toolbar_elements={researchToolbarElements}>
                          <VerifiedMatches/>
                      </Layout>
                  </Route>
                  <Route path="/results">
                      <Layout toolbar_elements={researchToolbarElements}>
                          <Results/>
                      </Layout>
                  </Route>
                  <Route path="/matcher">
                      <Layout toolbar_elements={researchToolbarElements}>
                          <Matcher/>
                      </Layout>
                  </Route>
                  <Route path="/dataset_fabrication">
                      <Layout toolbar_elements={dataLakeToolbarElements}>
                          <DatasetFabrication/>
                      </Layout>
                  </Route>
                  <Route path="/get_fabricated">
                      <Layout toolbar_elements={dataLakeToolbarElements}>
                          <GetFabricated/>
                      </Layout>
                  </Route>
                  <Route path="/algorithm_evaluation">
                      <Layout toolbar_elements={dataLakeToolbarElements}>
                          <AlgorithmEvaluation/>
                      </Layout>
                  </Route>
                  <Route path="/evaluation_results">
                      <Layout toolbar_elements={dataLakeToolbarElements}>
                          <EvaluationResults/>
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
