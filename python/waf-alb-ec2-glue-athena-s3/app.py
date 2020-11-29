from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_wafv2 as wafv2,
    core,
)


class LoadBalancerStack(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

        vpc = ec2.Vpc(self, "VPC")

        data = open("./httpd.sh", "rb").read()
        httpd = ec2.UserData.for_linux()
        httpd.add_commands(str(data, 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            user_data=httpd,
        )

        lb = elbv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=vpc,
            internet_facing=True)

        listener = lb.add_listener("Listener", port=80)
        listener.add_targets("Target", port=80, targets=[asg])
        listener.connections.allow_default_port_from_any_ipv4("Open to the world")

        asg.scale_on_request_count("AModestLoad", target_requests_per_second=1)
        core.CfnOutput(self, "LoadBalancer", export_name="LoadBalancer", value=lb.load_balancer_dns_name)

        # === #
        # WAF #
        # === #

        # TODO #10 apply the web_acl to a resource
        # no method to apply the web_acl to a resource in version 1.75.0
        web_acl = wafv2.CfnWebACL(
            scope_=self,
            id="waf",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(),
            scope="REGIONAL",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="waf-web-acl",
                sampled_requests_enabled=True
            )
        )


def main():
    app = core.App()
    LoadBalancerStack(app, "LoadBalancerStack")
    app.synth()


if __name__ == "__main__":
    main()
