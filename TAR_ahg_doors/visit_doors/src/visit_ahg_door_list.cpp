
#include "plan_execution/ExecutePlanAction.h"

#include <actionlib/client/simple_action_client.h>

#include <ros/ros.h>

//add move base goal

typedef actionlib::SimpleActionClient<plan_execution::ExecutePlanAction> Client;

using namespace std;

int main(int argc, char**argv) {
  ros::init(argc, argv, "visit_door_list");
  ros::NodeHandle n;

  ros::NodeHandle privateNode("~");
  string door_name;
  nh.getParam("door", door_name);  
  /*string locationA;
  privateNode.param<string>("a",locationA,"d3_414b1");

  string locationB
  privateNode.param<string>("b",locationB,"d3_414b2");*/
  
  std::vector<string> doors;
  
  doors.push_back(door_name);
  //doors.push_back("d3_418");
  
  int current_door = 0;

  Client client("/plan_executor/execute_plan", true);
  client.waitForServer();

  bool fromAtoB = true;

  //and input is true
  while (ros::ok()) {

    // string location = doors.at(current_door);
    // current_door++;
    // if (current_door >= (int)doors.size())
    //     current_door = 0;

    ROS_INFO_STREAM("going to " << door_name);

    plan_execution::ExecutePlanGoal goal;
    //move base goal

    //just publish twist message????!?!?!?!!?!?!?!?
    //publish a twist velocity as 0 because technically the bot is still moving towards the goal
    //the pace is 0 so its "not moving"

    plan_execution::AspRule rule;
    plan_execution::AspFluent fluent;
    fluent.name = "not is_near_name";
    
    //if input is true, push back door destination, else go back to start
    
    //start position???

    fluent.variables.push_back("1");
    fluent.variables.push_back("\"" + door_name + "\"");

    rule.body.push_back(fluent);
    goal.aspGoal.push_back(rule);

    ROS_INFO("sending goal");
    client.sendGoalAndWait(goal);

    if (client.getState() == actionlib::SimpleClientGoalState::ABORTED) {
      ROS_INFO("Aborted");
    } else if (client.getState() == actionlib::SimpleClientGoalState::PREEMPTED) {
      ROS_INFO("Preempted");
    }

    else if (client.getState() == actionlib::SimpleClientGoalState::SUCCEEDED) {
      ROS_INFO("Succeeded!");
    } else
      ROS_INFO("Terminated");

  }

  return 0;
}

