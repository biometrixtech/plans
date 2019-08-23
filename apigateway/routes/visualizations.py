

def get_visualization_parameter(request):

    visualizations = True

    if 'visualizations' in request.json:
        visualization_request = request.json['visualizations']
        try:
            visualizations = bool(visualization_request)
        except:
            pass
    return visualizations